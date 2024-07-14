# Premium Bot Setup Guide

This guide will help you set up the Premium Bot on your system. Follow these steps to install the necessary dependencies and configure the required services.

## Prerequisites

Ensure the following are installed on your system:

- Python 3
- `pip` (Python package installer)
- `curl`

## Installation Steps

### 1. Clone the Repository

Clone the Premium Bot repository to your local machine and navigate to the directory.

```bash
git clone https://github.com/padra1386/Premium-Bot.git
cd Premium-Bot
```

### 2. Install Python Dependencies

Install the required Python packages using `pip`.

```bash
pip install -r requirements.txt
```

### 3. Set Up PostgreSQL

Update your package lists and install PostgreSQL along with the necessary extensions.

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

Start the PostgreSQL service.

```bash
sudo systemctl start postgresql.service
```

Create a new PostgreSQL user and database for Premium Bot.

```bash
sudo -u postgres createuser --interactive
sudo -u postgres createdb premiumbot
```

### 4. Add a New System User

Add a new user to your system (replace `padra` with your desired username).

```bash
sudo adduser your-name
```

### 5. Set Up Redis

Add the Redis GPG key and repository to your system.

```bash
curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list
```

Update your package lists and install Redis.

```bash
sudo apt-get update
sudo apt-get install redis
```

### 6. Customize The .env File

Customize the .env file with you're own data

```bash
token=xxx
db_host="xxx"
db_name="xxx"
db_user="xxx"
db_password="xxx"
db_port=xxx
three_m_usd_price=xxx
nine_m_usd_price=xxx
twelve_m_usd_price=xxx
fee_amount=xxx
profit_amount=xxx
admin_chat_id=xxx
```

### 7. Run the Bot

Run the following scripts to start the Premium Bot.

```bash
python3 currencyapi.py
python3 main.py
```

## Additional Information

For more details on configuring and customizing the Premium Bot, refer to the documentation provided in the repository.

## Troubleshooting

If you encounter any issues during installation or setup, refer to the troubleshooting section in the documentation or raise an issue on the [GitHub repository](https://github.com/padra1386/Premium-Bot/issues).
