#!/usr/bin/env python3
"""
Script para criar arquivo de configuração de email a partir de variáveis de ambiente
Usado pelo GitHub Actions workflow
"""
import json
import os
import sys

def main():
    """Criar arquivo de configuração de email"""
    os.makedirs('data', exist_ok=True)
    
    # Get values from environment variables (safely handles special characters)
    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port_str = os.environ.get('SMTP_PORT', '587')
    smtp_port = int(smtp_port_str) if smtp_port_str.isdigit() else 587
    email = os.environ.get('SENDER_EMAIL', '')
    password = os.environ.get('SENDER_PASSWORD', '')
    to_email = os.environ.get('RECEIVER_EMAIL', '')
    
    # Validate required fields
    if not email or not password or not to_email:
        print("❌ Missing required email secrets: SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL")
        sys.exit(1)
    
    # Create config in the format expected by EmailSender
    # File: data/email_config.json (not data/config.json)
    # Structure: flat (not nested)
    # Fields: email, password, to_email (not sender_email, sender_password, receiver_email)
    config = {
        'smtp_server': smtp_server,
        'smtp_port': smtp_port,
        'email': email,
        'password': password,
        'to_email': to_email,
        'use_tls': True
    }
    
    config_file = 'data/email_config.json'
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    
    print('✅ Email config created from secrets')
    print(f'   File: {config_file}')
    print(f'   From: {email}')
    print(f'   To: {to_email}')

if __name__ == '__main__':
    main()

