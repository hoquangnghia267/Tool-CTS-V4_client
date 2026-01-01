import os
import subprocess
import sys
import time
import mysql.connector
import logging
import tkinter as tk
from tkinter import messagebox
import requests
from datetime import datetime, timezone, timedelta
from cryptography.hazmat.primitives.hashes import SHA256, SHA1
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding as asymmetric_padding
from cryptography.x509 import load_pem_x509_certificate, ocsp, ExtensionOID, AuthorityInformationAccessOID, oid
from cryptography.x509.oid import AuthorityInformationAccessOID, ExtendedKeyUsageOID
from cryptography.x509.ocsp import OCSPRequestBuilder, OCSPCertStatus, OCSPResponseStatus, load_der_ocsp_response

# --- Helper Functions ---

def get_text_data(text_widget):
    """Gets multiline text from a Text widget and returns it as a list of strings."""
    return text_widget.get("1.0", tk.END).strip().split('\n')

def get_text_single(text_widget):
    """Gets all text from a Text widget and returns it as a single stripped string."""
    return text_widget.get("1.0", tk.END).strip()

def hex_to_decimal(hex_string):
    """Converts a single hex string to a decimal integer."""
    try:
        return int(hex_string, 16)
    except (ValueError, TypeError):
        return None

def decimal_to_hex(decimal_number):
    """Converts a single decimal number to a hex string."""
    try:
        return format(int(decimal_number), 'X')
    except (ValueError, TypeError):
        return None

def setup_logging(section_name, base_log_dir="log"):
    """Sets up logging to a file in a structured directory like log/YYYY/MM/section.log."""
    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")

    log_dir = os.path.join(base_log_dir, year, month)
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, f"{section_name}.log")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    logger = logging.getLogger(section_name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        logger.addHandler(file_handler)
        logger.propagate = False
    return logger

def extract_common_name(subject):
    """Extracts the Common Name (CN) from a certificate subject string."""
    try:
        return subject.split("CN=")[1].split(",")[0]
    except IndexError:
        return "N/A"

def extract_uid(subject):
    """Extracts the UID from a certificate subject string."""
    try:
        return subject.split("UID=")[1].split(")")[0]
    except IndexError:
        return "N/A"

# --- OCSP Functions ---

def check_certificate_status(cert_path, issuer_path, result_text):
    """Performs an OCSP check for the given certificate."""
    if not cert_path or not issuer_path:
        messagebox.showwarning("Warning", "Please select both a certificate and an issuer file.")
        return
    try:
        with open(cert_path, "rb") as cert_file, open(issuer_path, "rb") as issuer_file:
            pem_cert = cert_file.read()
            pem_issuer = issuer_file.read()

        cert = load_pem_x509_certificate(pem_cert)
        issuer = load_pem_x509_certificate(pem_issuer)

        def get_ocsp_server(cert):
            try:
                aia = cert.extensions.get_extension_for_oid(ExtensionOID.AUTHORITY_INFORMATION_ACCESS).value
                ocsps = [ia for ia in aia if ia.access_method == AuthorityInformationAccessOID.OCSP]
                if not ocsps:
                    raise ValueError('No OCSP server entry in AIA')
                return ocsps[0].access_location.value
            except Exception as e:
                raise ValueError(f"Failed to extract OCSP URL: {e}")

        builder = OCSPRequestBuilder().add_certificate(cert, issuer, hashes.SHA1()) # Using SHA1 as per original code
        req = builder.build()
        ocsp_server_url = get_ocsp_server(cert)

        response = requests.post(
            ocsp_server_url,
            data=req.public_bytes(serialization.Encoding.DER),
            headers={'Content-Type': 'application/ocsp-request'},
            timeout=10
        )
        response.raise_for_status()

        ocsp_resp = load_der_ocsp_response(response.content)
        result_lines = ["----- OCSP Responder -----"]
        result_lines.append(f"Response Status: {ocsp_resp.response_status.name}")
        
        if ocsp_resp.response_status == OCSPResponseStatus.SUCCESSFUL:
            cert_status = ocsp_resp.certificate_status
            result_lines.append(f"Certificate Status: {cert_status.name if cert_status else 'UNKNOWN'}")
            
            if cert_status == OCSPCertStatus.REVOKED:
                revocation_time = ocsp_resp.revocation_time + timedelta(hours=7)
                result_lines.append(f"Revocation Time: {revocation_time.strftime('%Y-%m-%d %H:%M:%S')}")
                if ocsp_resp.revocation_reason:
                    result_lines.append(f"Revocation Reason: {ocsp_resp.revocation_reason.name}")

            this_update = ocsp_resp.this_update + timedelta(hours=7)
            result_lines.append(f"This Update: {this_update.strftime('%Y-%m-%d %H:%M:%S')}")
            result_lines.append(f"OCSP URI: {ocsp_server_url}")
        
        result_lines.append("\n----- Certificate Information -----")
        result_lines.append(f"Subject: {extract_common_name(str(cert.subject))}") 
        result_lines.append(f"UID: {extract_uid(str(cert.subject))}")  
        result_lines.append(f"Serial Number: {decimal_to_hex(cert.serial_number)}")  
        result_lines.append(f"Valid from: {cert.not_valid_before.strftime('%Y-%m-%d %H:%M:%S')}")
        result_lines.append(f"Valid to: {cert.not_valid_after.strftime('%Y-%m-%d %H:%M:%S')}")

        result_str = "\n".join(result_lines)
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, result_str)
        result_text.config(state=tk.DISABLED)

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during OCSP check: {e}")

#-----TMS1 Functions-----
def get_info_TMS1(conn, tokenid, get_result_text):
    if not tokenid:
        messagebox.showwarning("Warning", "Please enter a Token ID.")
        return
    try:
        cursor = conn.cursor()
        query = "SELECT isPushNotice, MST, SubjectName, NoticeInfo, IsBlock, IsUnblock FROM token WHERE TokenID = %s;"
        cursor.execute(query, (tokenid,))
        results = cursor.fetchall()
        if results:
            result_str = ""
            for row in results:
                isPushNotice, MST, SubjectName, NoticeInfo, IsBlock, IsUnblock = row
                result_str += f"Token ID: {tokenid}\n"
                result_str += f"MST: {MST}\n"
                result_str += f"Tên công ty: {SubjectName}\n"
                result_str += f"IsUnblock: {IsUnblock}\n"
                result_str += f"Trạng thái thông báo: {'ON' if isPushNotice == 1 else 'OFF'}\n"
                result_str += f"Trạng thái khóa: {'ON' if IsBlock == 1 else 'OFF'}\n"
                result_str += f"Câu thông báo:\n{NoticeInfo}\n"
                
            get_result_text.config(state=tk.NORMAL)
            get_result_text.delete(1.0, tk.END)
            get_result_text.insert(tk.END, result_str)
            get_result_text.config(state=tk.DISABLED)
        else:
            messagebox.showinfo("Thông báo", "Không tìm thấy Token ID đã nhập.")       
        cursor.close()
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))

def note_hotro_tms1(conn, token_hid, content_text, logger):
    if not token_hid or not content_text:
        messagebox.showwarning("Warning", "Token list and content cannot be empty.")
        return
    try:
        cursor = conn.cursor()
        id_list = "','".join(token_hid)
        sql = f"UPDATE token SET isPushNotice=0, NoticeInfo = %s WHERE TokenID IN ('{id_list}')"
        cursor.execute(sql, (content_text,))
        conn.commit()
        logger.info(f"{token_hid} - ON note page: hotro.smartsign.com.vn\n")
        messagebox.showinfo("Success", f"{cursor.rowcount} records updated successfully")
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))

def notifications_tms1(conn, token_hid, content_text, logger):
    if not token_hid or not content_text:
        messagebox.showwarning("Warning", "Token list and content cannot be empty.")
        return
    try:
        cursor = conn.cursor()
        id_list = "','".join(token_hid)
        sql = f"UPDATE token SET isPushNotice=1, NoticeInfo = %s WHERE TokenID IN ('{id_list}')"
        cursor.execute(sql, (content_text,))
        conn.commit()
        logger.info(f"{token_hid} - ON Notifications TMS1 \n")
        messagebox.showinfo("Success", f"{cursor.rowcount} records updated successfully")
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))

def off_notifications_tms1(conn, token_hid, logger):
    if not token_hid:
        messagebox.showwarning("Warning", "Token list cannot be empty.")
        return
    try:
        cursor = conn.cursor()
        id_list = "','".join(token_hid)
        sql = f"UPDATE token SET isPushNotice = NULL, NoticeInfo = NULL WHERE TokenID IN ('{id_list}')"
        cursor.execute(sql)
        conn.commit()
        logger.info(f"{token_hid} - OFF Notifications TMS1 \n")
        messagebox.showinfo("Success", f"{cursor.rowcount} records updated successfully")
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))

def block_tms1(conn, token_hid, note_text, logger):
    if not token_hid or not note_text:
        messagebox.showwarning("Warning", "Token list and note cannot be empty.")
        return
    try:
        cursor = conn.cursor()
        id_list = "','".join(token_hid)
        sql = f"UPDATE token SET IsBlock = 1, isPushNotice = 1, NoticeInfo = %s WHERE TokenID IN ('{id_list}')"
        cursor.execute(sql, (note_text,))
        conn.commit()
        logger.info(f"{token_hid} - block \n")
        messagebox.showinfo("Success", f"{cursor.rowcount} records updated successfully")
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))

def unblock_tms1(conn, token_hid, logger):
    if not token_hid:
        messagebox.showwarning("Warning", "Token list cannot be empty.")
        return
    try:
        cursor = conn.cursor()
        id_list = "','".join(token_hid)
        sql = f"UPDATE token SET IsUnblock = 1, isPushNotice = NULL, NoticeInfo = NULL WHERE TokenID IN ('{id_list}')"
        cursor.execute(sql)
        conn.commit()
        logger.info(f"{token_hid} - unblock \n")
        messagebox.showinfo("Success", f"{cursor.rowcount} records updated successfully")
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))

def uninitialize_tms1(conn, token_id, logger):
    """Sets IsUnblock to 0 and isInitialize to NULL for a given Token ID."""
    if not token_id:
        messagebox.showwarning("Warning", "Token ID cannot be empty.")
        return
    try:
        cursor = conn.cursor()
        sql = "UPDATE token SET IsUnblock = 0, isInitialize = NULL WHERE TokenID = %s"
        cursor.execute(sql, (token_id,))
        
        if cursor.rowcount == 0:
            messagebox.showwarning("No Update", f"Token ID '{token_id}' not found or already in the desired state.")
        else:
            conn.commit()
            logger.info(f"Uninitialized Token ID: {token_id}")
            messagebox.showinfo("Success", f"Token ID '{token_id}' has been uninitialized.")
            
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()

#-----TMS2 Functions-----
def get_info_TMS2(conn, tokenid, get_result_text):
    if not tokenid:
        messagebox.showwarning("Warning", "Please enter a Token ID.")
        return
    try:
        cursor = conn.cursor()
        query = "SELECT use_specific_notification, token_block_status, token_title, token_notification, token_note FROM token_ms WHERE token_hid = %s;"
        cursor.execute(query, (tokenid,))
        results = cursor.fetchall()
        if results:
            result_str = ""
            for row in results:
                use_specific_notification, token_block_status, token_title, token_notification, token_note = row
                result_str += f"Token ID: {tokenid}\n"
                result_str += f"Trạng thái thông báo: {'ON' if use_specific_notification == 1 else 'OFF'}\n"
                result_str += f"Trạng thái khóa: {'ON' if token_block_status == 1 else 'OFF'}\n"
                result_str += f"Câu thông báo:\nTiêu đề: {token_title}\nNội dung: {token_notification}\n"
                result_str += f"Note: {token_note}"

            get_result_text.config(state=tk.NORMAL)
            get_result_text.delete(1.0, tk.END)
            get_result_text.insert(tk.END, result_str)
            get_result_text.config(state=tk.DISABLED)
        else:
            messagebox.showinfo("Thông báo", "Không tìm thấy Token ID đã nhập.")       
        cursor.close()
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))

def block_tms2(conn, token_hid, note_text, logger):
    if not token_hid or not note_text:
        messagebox.showwarning("Warning", "Token list and note cannot be empty.")
        return
    try:
        cursor = conn.cursor()
        id_list = "','".join(token_hid)
        sql = f"UPDATE token_ms SET token_block_status = 1, token_note = %s WHERE token_hid IN ('{id_list}')"
        cursor.execute(sql, (note_text,))
        conn.commit()
        logger.info(f"{token_hid} - block \n")
        messagebox.showinfo("Success", f"{cursor.rowcount} records updated successfully")
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))

def unblock_tms2(conn, token_hid, logger):
    if not token_hid:
        messagebox.showwarning("Warning", "Token list cannot be empty.")
        return
    try:
        cursor = conn.cursor()
        id_list = "','".join(token_hid)
        sql = f"UPDATE token_ms SET token_block_status = 0, token_note = NULL WHERE token_hid IN ('{id_list}')"
        cursor.execute(sql)
        conn.commit()
        logger.info(f"{token_hid} - unblock \n")
        messagebox.showinfo("Success", f"{cursor.rowcount} records updated successfully")
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))
  
def notifications_tms2(conn, token_hid, title_text, content_text, logger):
    if not all([token_hid, title_text, content_text]):
        messagebox.showwarning("Warning", "Token list, title, and content cannot be empty.")
        return
    try:
        cursor = conn.cursor()
        id_list = "','".join(token_hid)
        sql = """
            UPDATE token_ms 
            SET use_specific_notification = 1, 
                token_notification_status = 1, 
                token_valid_from = CURDATE(),
                token_valid_to = '2025-05-19 23:59:59', 
                token_title = %s, 
                token_notification = %s 
            WHERE token_hid IN ('{id_list}')
        """
        cursor.execute(sql, (title_text, content_text))
        conn.commit()
        logger.info(f"{token_hid} - ON Notifications TMS2 \n")
        messagebox.showinfo("Success", f"{cursor.rowcount} records updated successfully")
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))

def off_notifications_tms2(conn, token_hid, logger):
    if not token_hid:
        messagebox.showwarning("Warning", "Token list cannot be empty.")
        return
    try:
        cursor = conn.cursor()
        id_list = "','".join(token_hid)
        sql = """
            UPDATE token_ms 
            SET use_specific_notification = NULL, 
                token_notification_status = 0, 
                token_valid_from = NULL, 
                token_valid_to = NULL, 
                token_title = NULL, 
                token_notification = NULL 
            WHERE token_hid IN ('{id_list}')
        """
        cursor.execute(sql)
        conn.commit()
        logger.info(f"{token_hid} - OFF Notifications TMS2 \n")
        messagebox.showinfo("Success", f"{cursor.rowcount} records updated successfully")
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))