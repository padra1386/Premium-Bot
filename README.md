# Premium Bot Setup Guide 📝

This guide will help you set up the Premium Bot on your system. Follow these steps to install the necessary dependencies and configure the required services.

## Prerequisites

Ensure the following are installed on your system:

- Python 3
- `pip` (Python package installer)
- Docker (for containerization)

## Installation Steps 🔧💻

### 1. Clone the Repository

Clone the Premium Bot repository to your local machine and navigate to the directory.

```bash
git clone https://github.com/padra1386/Premium-Bot.git
cd Premium-Bot
```
### 2. Crate And Customize The .env File

Create a new .env and Customize with your desired data

```bash
token=your-telegram-bot-token
db_name="your-db-name"
db_user="your-user"
db_password="your-password"
db_port=5432
three_m_usd_price=your-preferred-price
nine_m_usd_price=your-preferred-price
twelve_m_usd_price=your-preferred-price
fee_amount=your-preferred-price
profit_amount=your-preferred-price
admin_chat_id=your-admin-chat-id
```

### 3. Build and Start Docker Containers

Build and start the Docker containers using Docker Compose.

```bash
docker-compose build
docker-compose up
```

## Troubleshooting

If you encounter any issues during installation or setup, refer to the troubleshooting section in the documentation or raise an issue on the [GitHub repository](https://github.com/padra1386/Premium-Bot/issues).
```
