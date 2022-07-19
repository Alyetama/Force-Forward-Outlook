# Force Forward Outlook

For when your IT admin is blocking automatic email forwarding outside your organization, but you want to do it anyway.


## Requirements
- [Python>=3.6](https://www.python.org/downloads/)
- [Rclone](https://rclone.org/downloads/)


## Setup

### Step 1

1. Clone this repository:

```sh
git clone https://github.com/Alyetama/Force-Forward-Outlook.git
cd Force-Forward-Outlook
```

2. Install dependencies:

- If you want to use Docker, skip this step.

```sh
pip install -r requirements.txt
```

### Step 2

1. Download and install `Rclone` if you haven't already. Then, create a new remote if you don't have one.

```sh
rclone config create mydrive drive
```

2. Create directories `emails/sent`:

```sh
# Replace `mydrive` with your actual remote name if different
rclone mkdir mydrive:emails/sent
```

### Step 3

1. Log in to your outlook account, then go to [Microsoft Power Automate](https://us.flow.microsoft.com/en-us/).
2. Click `+ Create` -> `Automated cloud flow` -> pick a name -> under `Choose your flow's trigger` search `When a new email arrives` (**make sure to select the correct service!** If you have a school/work email, it's probably `Office 365 Outlook`, otherwise, `Outlook`).
3. Click `Create`, then sign in to your Outlook email account and select `Inbox` under `Folder`.
4. Add a new step, then search for the cloud storage provider that you used for rclone (e.g., Google Drive) -> select `Create File`.
5. Under `Folder path` type: `emails`. Under `File name` click on `Add dynamic content`, then search and select `Message Id`. Under `File content`, click on `Add dynamic content`, then search and select `Body` (the one that starts with a capital letter).
6. Save, then test your workflow to make sure everything is setup correctly.

### Step 4

1. In the repository directory, rename `.env.example` to `.env`:

```sh
mv .env.example .env
```

2. Then open it in your favorite text editor and fill out the variables value.

- `FROM_EMAIL`: The email you want to send from (**use a Gmail address here!**).
- `FROM_EMAIL_PASSWORD`: The password of the email you want to send from (see note bleow)*.
- `TO_EMAIL`: Your outlook email address where automatic forwarding is disabled.
- `REMOTE_NAME`: The name of the rclone remote you used in [Step 2](#step-2) (e.g., `mydrive`).

**\*Important note: `FROM_EMAIL_PASSWORD` should not be your standrad email password! Use an [app password](https://support.google.com/accounts/answer/185833?hl=en) instead.**

## Usage

```sh
python forwardgod.py
# or in the background:
nohup python forwardgod.py &
```


## Docker

```sh
docker run -d --env-file .env \
    -v "$(dirname $(rclone config file | tail -1))":/root/.config/rclone \
    alyetama/force-forward-outlook:latest
```
