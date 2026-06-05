import argparse
import requests
from urllib.parse import quote

AUTH0_DOMAIN = "dev-24uc0lfu7st66b7k.us.auth0.com"  # example: dev-abc123.us.auth0.com
CLIENT_ID = "PXa9EvwLYOTMeyVcvf0lY34tAZJ1joiB"
CLIENT_SECRET = "Ae8bl0fqwT2MN3EmBHV7Km9OMr7JLsR-y4bMsg_oP00zKWZtLO7g_6qtSPfpBZE7"

CONNECTION = "Username-Password-Authentication"


def auth0_request(method, url, **kwargs):
    try:
        response = requests.request(method, url, timeout=20, **kwargs)
    except requests.RequestException as error:
        raise SystemExit(f"Auth0 request failed before receiving a response: {error}") from error

    if not response.ok:
        print(f"Auth0 request failed: {response.status_code}")
        error_body = None

        try:
            error_body = response.json()
            print(error_body)
        except ValueError:
            print(response.text)

        if response.status_code == 409:
            raise SystemExit(
                "Create failed because that user already exists. "
                "Use a different email address, or use the update command for the existing user."
            )

        message = error_body.get("message") if isinstance(error_body, dict) else response.text
        raise SystemExit(f"Auth0 request failed with status {response.status_code}: {message}")

    if response.status_code == 204 or not response.content:
        return None

    return response.json()


def get_management_token():
    domain = AUTH0_DOMAIN.removeprefix("https://").rstrip("/")
    base_url = f"https://{domain}"

    data = auth0_request(
        "POST",
        f"{base_url}/oauth/token",
        json={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "audience": f"{base_url}/api/v2/",
            "grant_type": "client_credentials",
        },
    )

    return data["access_token"], base_url


def management_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def create_user(email, password, name=None, nickname=None):
    token, base_url = get_management_token()
    payload = {
        "email": email,
        "password": password,
        "connection": CONNECTION,
        "email_verified": False,
    }

    if name:
        payload["name"] = name

    if nickname:
        payload["nickname"] = nickname

    return auth0_request(
        "POST",
        f"{base_url}/api/v2/users",
        headers=management_headers(token),
        json=payload,
    )


def update_user(user_id, updates):
    token, base_url = get_management_token()
    encoded_user_id = quote(user_id, safe="")

    return auth0_request(
        "PATCH",
        f"{base_url}/api/v2/users/{encoded_user_id}",
        headers=management_headers(token),
        json=updates,
    )


def delete_user(user_id):
    token, base_url = get_management_token()
    encoded_user_id = quote(user_id, safe="")

    return auth0_request(
        "DELETE",
        f"{base_url}/api/v2/users/{encoded_user_id}",
        headers=management_headers(token),
    )


def parse_boolean(value):
    value = value.lower()

    if value in ("true", "t", "yes", "y", "1"):
        return True

    if value in ("false", "f", "no", "n", "0"):
        return False

    raise argparse.ArgumentTypeError("Use true or false.")


def build_parser():
    parser = argparse.ArgumentParser(
        description="Create, update, or delete Auth0 users with the Management API."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser("create", help="Create a new Auth0 user.")
    create_parser.add_argument("--email", required=True, help="Email for the new user.")
    create_parser.add_argument("--password", required=True, help="Password for the new user.")
    create_parser.add_argument("--name", help="Full name for the new user.")
    create_parser.add_argument("--nickname", help="Nickname for the new user.")

    update_parser = subparsers.add_parser("update", help="Update an existing Auth0 user.")
    update_parser.add_argument("--user-id", required=True, help="Auth0 user ID, like auth0|abc123.")
    update_parser.add_argument("--email", help="New email address.")
    update_parser.add_argument("--email-verified", type=parse_boolean, help="Set to true or false.")
    update_parser.add_argument("--name", help="New full name.")
    update_parser.add_argument("--nickname", help="New nickname.")

    delete_parser = subparsers.add_parser("delete", help="Delete an existing Auth0 user.")
    delete_parser.add_argument("--user-id", required=True, help="Auth0 user ID, like auth0|abc123.")
    delete_parser.add_argument("--yes", action="store_true", help="Skip the confirmation prompt.")

    return parser


def handle_create(args):
    user = create_user(
        email=args.email,
        password=args.password,
        name=args.name,
        nickname=args.nickname,
    )
    print("Created user:")
    print(user)


def handle_update(args):
    updates = {}

    if args.email:
        updates["email"] = args.email

    if args.email_verified is not None:
        updates["email_verified"] = args.email_verified

    if args.name:
        updates["name"] = args.name

    if args.nickname:
        updates["nickname"] = args.nickname

    if not updates:
        raise SystemExit("Nothing to update. Add --email, --email-verified, --name, or --nickname.")

    user = update_user(args.user_id, updates)
    print("Updated user:")
    print(user)


def handle_delete(args):
    if not args.yes:
        confirmation = input(f"Delete user {args.user_id}? Type DELETE to confirm: ")
        if confirmation != "DELETE":
            print("Delete canceled.")
            return

    delete_user(args.user_id)
    print(f"Deleted user: {args.user_id}")


if __name__ == "__main__":
    parsed_args = build_parser().parse_args()

    if parsed_args.command == "create":
        handle_create(parsed_args)
    elif parsed_args.command == "update":
        handle_update(parsed_args)
    elif parsed_args.command == "delete":
        handle_delete(parsed_args)
