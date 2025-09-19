## Team Name:DEVSQUAD

## Project Description

This project is a fullstack application that takes MoMo SMS data in XML format, cleans and organizes it, then stores it in a database. The system categorizes transactions like deposits, withdrawals, and payments, making the data easier to understand. On top of that, it provides a simple dashboard interface where users can explore charts and insights to analyze their financial activity.

## Group Members
- **Aime Ndayambaje** – [@aimelive](https://github.com/aimelive)  
- **Ngororano Armstrong** – [@capitale1](https://github.com/capitale1)  

 ## Scrum Board

We are using a GitHub Project board to manage our tasks with Agile methodology.  
You can view our Scrum board here: [DEVSQUAD Scrum Board](https://github.com/users/aimelive/projects/2)

## Project Structure

├── README.md # Setup, overview
├── docs/ # Documentation
├── database/
│ └── database_setup.sql # SQL schema + sample data
├── .env.example # Environment variables
├── requirements.txt # Python dependencies
├── index.html # Dashboard entry (static)
├── web/ # Dashboard frontend (CSS, JS, assets)
├── data/
│ ├── raw/ # Input XML
│ ├── processed/ # Cleaned / aggregated JSON
│ ├── db.sqlite3 # SQLite DB
│ └── logs/ # ETL logs and dead letters
├── etl/ # ETL scripts (parse, clean, categorize, load)
├── api/ # Optional FastAPI endpoints
├── scripts/ # Shell scripts to run ETL, export JSON, serve frontend
└── tests/ # Unit tests

## High-Level System Architecture

Here is our system architecture diagram click on it and it takes you directly to its path file:

![System Architecture](web/assets/my%20arctechure.jpg)

## Database Design Overview

The database supports the processing of MoMo SMS data by separating raw messages from parsed transactions.
Key tables include:

messages – Stores every SMS exactly as received, including metadata and the full message body.

transactions – Holds structured details parsed from messages (amounts, sender/receiver, timestamps).

categories – Lookup table of transaction categories such as deposit, payment, or transfer.

transaction_category_link – Junction table to handle the many-to-many relationship between transactions and categories.

system_logs – Tracks ETL runs, errors, and processing context for transparency and troubleshooting.

This structure ensures:

Data integrity through primary/foreign key constraints.

Auditability by preserving the original SMS content.

Scalability for future dashboard queries and analytics.

![ERD](web/assets/ERD.png)

## database documentation
[Database Design Document](docs/Database%20Design%20Document%20(2).pdf)

## AI Assistance Disclosure

Language editing and formatting of this README were improved with the help of ChatGPT (OpenAI, 2025).
All database tables, relationships, SQL scripts, and business rules were independently designed and implemented by the DEVSQUAD team without AI generation.
