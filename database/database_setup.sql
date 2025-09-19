-- database_setup.sql
-- MySQL DDL + sample DML for MoMo SMS Processing
-- Author: DEVSQUAD Team (Aime Ndayambaje & Ngororano Armstrong)
-- NOTE: Grammar and formatting of this documentation
-- were proof-read with the help of ChatGPT (OpenAI).
-- All database tables, relationships, and sample data
-- were fully designed and implemented by the DEVSQUAD team.


DROP DATABASE IF EXISTS momodemo;
CREATE DATABASE momodemo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE momodemo;

-- =====================================================
-- Table: messages
-- Purpose: Store every raw SMS exactly as received so
--we can re-process data if parsing rules change.
-- =====================================================
CREATE TABLE messages (
    sms_id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Internal numeric key',
    protocol VARCHAR(16) COMMENT 'Protocol flag from XML',
    address VARCHAR(64) NOT NULL COMMENT 'Sender or service name',
    date BIGINT NOT NULL COMMENT 'Epoch time from XML date attribute',
    date_sent BIGINT NULL COMMENT 'Epoch time from XML date_sent attribute',
    type TINYINT COMMENT '1 = inbox, 2 = sent',
    service_center VARCHAR(64) NULL COMMENT 'SMS service center',
    body TEXT COMMENT 'Full SMS text',
    readable_date VARCHAR(64) NULL COMMENT 'Human readable date',
    contact_name VARCHAR(128) NULL COMMENT 'Optional contact name',
    processed_json JSON NULL COMMENT 'Optional JSON after ETL',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_messages_date (date),
    INDEX idx_messages_address (address(32))
) ENGINE=InnoDB;

-- =====================================================
-- Table: transactions
-- Purpose: Parsed financial details extracted from messages.
-- =====================================================
CREATE TABLE transactions (
    transaction_id VARCHAR(64) PRIMARY KEY COMMENT 'MoMo TxId or generated UUID',
    sms_id INT NULL COMMENT 'References the source SMS',
    amount DECIMAL(18,2) NOT NULL COMMENT 'Transaction amount in RWF',
    currency VARCHAR(8) DEFAULT 'RWF' COMMENT 'Currency code',
    tx_type VARCHAR(32) NOT NULL COMMENT 'deposit, payment, transfer, etc.',
    sender_name VARCHAR(128) NULL,
    sender_msisdn VARCHAR(32) NULL,
    receiver_name VARCHAR(128) NULL,
    receiver_msisdn VARCHAR(32) NULL,
    balance_after DECIMAL(18,2) NULL COMMENT 'Wallet balance after txn',
    fee DECIMAL(18,2) DEFAULT 0 COMMENT 'Transaction fee',
    tx_timestamp DATETIME NULL COMMENT 'Parsed transaction time',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_tx_sms FOREIGN KEY (sms_id)
        REFERENCES messages(sms_id) ON DELETE SET NULL,
    INDEX idx_tx_timestamp (tx_timestamp),
    INDEX idx_tx_type (tx_type)
) ENGINE=InnoDB;

-- Restrict tx_type to known values (MySQL 8+ supports CHECK)
ALTER TABLE transactions
    ADD CONSTRAINT chk_tx_type
    CHECK (tx_type IN ('deposit','payment','transfer','withdrawal','airtime','other'));

-- =====================================================
-- Table: categories
-- Purpose: Lookup table for transaction categories.
-- =====================================================
CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(64) NOT NULL UNIQUE COMMENT 'e.g., deposit, merchant_payment',
    description TEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- =====================================================
-- Table: transaction_category_link
-- Purpose: Junction table to resolve many-to-many relation
--          between transactions and categories.
-- =====================================================
CREATE TABLE transaction_category_link (
    transaction_id VARCHAR(64) NOT NULL,
    category_id INT NOT NULL,
    PRIMARY KEY (transaction_id, category_id),
    CONSTRAINT fk_tcl_tx FOREIGN KEY (transaction_id)
        REFERENCES transactions(transaction_id) ON DELETE CASCADE,
    CONSTRAINT fk_tcl_cat FOREIGN KEY (category_id)
        REFERENCES categories(category_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- =====================================================
-- Table: system_logs
-- Purpose: Track ETL processing steps and errors.
-- =====================================================
CREATE TABLE system_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    level VARCHAR(16) NOT NULL COMMENT 'INFO, WARN, ERROR',
    message TEXT NOT NULL COMMENT 'Details of the log event',
    sms_id INT NULL COMMENT 'Optional reference to related SMS',
    context JSON NULL COMMENT 'Extra context such as run_id or stage',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_logs_sms FOREIGN KEY (sms_id)
        REFERENCES messages(sms_id) ON DELETE SET NULL,
    INDEX idx_logs_level (level)
) ENGINE=InnoDB;

-- =====================================================
-- Sample Data (at least 5 rows per main table)
-- NOTE: Example values created by the team from test XML.
-- =====================================================

INSERT INTO messages (protocol, address, date, date_sent, type, service_center, body, readable_date, contact_name)
VALUES
('0','M-Money',1715351458724,1715351451000,1,'+250788110381','You have received 2000 RWF from Jane Smith...','2024-05-10 16:30:58','(Unknown)'),
('0','M-Money',1715446129409,1715446122000,1,'+250788110381','TxId: 17818959211. Your payment of 2,000 RWF...','2024-05-11 18:48:49','(Unknown)'),
('0','M-Money',1715452495316,1715452487000,1,'+250788110381','*165*S*10000 RWF transferred to Samuel Carter...','2024-05-11 20:34:55','(Unknown)'),
('0','M-Money',1715513180213,1715513173000,1,'+250788110381','TxId: 45434420466. Your payment of 10,900 RWF...','2024-05-12 13:26:20','(Unknown)'),
('0','M-Money',1715713115618,1715713057000,1,'+250788110381','You have received 25000 RWF from Samuel Carter...','2024-05-14 20:58:35','(Unknown)');

INSERT INTO transactions (transaction_id, sms_id, amount, currency, tx_type,
                          sender_name, sender_msisdn, receiver_name, receiver_msisdn,
                          balance_after, fee, tx_timestamp)
VALUES
('76662021700', 1, 2000.00, 'RWF', 'deposit', 'Jane Smith', '250*******013', NULL, NULL, 2000.00, 0.00, '2024-05-10 16:30:51'),
('17818959211', 2, 2000.00, 'RWF', 'payment', NULL, NULL, 'Samuel Carter', '14965', 38400.00, 0.00, '2024-05-11 18:48:42'),
('TX-36521838-20240511-10000', 3, 10000.00, 'RWF', 'transfer', '36521838', NULL, 'Samuel Carter', '250791666666', 28300.00, 100.00, '2024-05-11 20:34:47'),
('45434420466', 4, 10900.00, 'RWF', 'payment', NULL, NULL, 'Jane Smith', '59543', 14380.00, 0.00, '2024-05-12 13:26:13'),
('43668074924', 5, 25000.00, 'RWF', 'deposit', 'Samuel Carter', '250*******013', NULL, NULL, 29060.00, 0.00, '2024-05-14 20:57:36');

INSERT INTO categories (name, description) VALUES
('deposit','Funds added to account'),
('payment','Payment to merchant or person'),
('transfer','Transfer between wallets or numbers'),
('withdrawal','Cash out via agent'),
('airtime','Airtime purchase or token');

INSERT INTO transaction_category_link (transaction_id, category_id) VALUES
('76662021700', 1),
('17818959211', 2),
('TX-36521838-20240511-10000', 3),
('45434420466', 2),
('43668074924', 1);

INSERT INTO system_logs (level, message, sms_id, context) VALUES
('INFO','Started ETL run', NULL, JSON_OBJECT('run_id','run-001')),
('INFO','Parsed SMS into transaction', 1, JSON_OBJECT('txn_id','76662021700')),
('WARN','Could not parse phone number fully, masked', 3, JSON_OBJECT('sms_id',3,'field','sender_msisdn')),
('ERROR','XML snippet failed validation, sent to dead_letter', NULL, JSON_OBJECT('file','momo.xml','line',200)),
('INFO','Exported processed dashboard.json', NULL, JSON_OBJECT('path','data/processed/dashboard.json'));

-- Optional view for quick reporting
CREATE VIEW v_tx_summary AS
SELECT t.transaction_id,
       t.tx_type,
       t.amount,
       t.tx_timestamp,
       m.address AS source,
       t.sender_msisdn,
       t.receiver_msisdn
FROM transactions t
LEFT JOIN messages m ON t.sms_id = m.sms_id;

