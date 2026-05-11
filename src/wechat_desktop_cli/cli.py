"""CLI entry point for wechat-desktop-cli."""
import argparse
import sys
import os
import json

def main():
    parser = argparse.ArgumentParser(
        description="WeChat Desktop CLI — Control WeChat via Win32 API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  wechat status                    Check if WeChat is running
  wechat send --to "阿锋"         Send a message
  wechat search "张三"             Search for a contact
        """
    )
    
    subparsers = parser.add_subparsers(dest="command")
    
    # status
    subparsers.add_parser("status", help="Check WeChat status")
    
    # send
    send_p = subparsers.add_parser("send", help="Send a message to a contact")
    send_p.add_argument("--to", "-t", required=True, help="Contact name or nickname")
    send_p.add_argument("--msg", "-m", default="😊", help="Message text (default: 😊)")
    
    # search
    search_p = subparsers.add_parser("search", help="Search for and open a contact")
    search_p.add_argument("name", help="Contact name to search")
    
    # activate
    subparsers.add_parser("activate", help="Bring WeChat window to front")
    
    args = parser.parse_args()
    
    # Import controller (only works on Windows with pywin32)
    try:
        from .controller import (
            get_status, activate_wechat, 
            search_contact, send_message
        )
    except (ImportError, OSError) as e:
        print(f"Error: This tool requires Windows with pywin32.\n{e}", file=sys.stderr)
        sys.exit(1)
    
    if args.command == "status":
        status = get_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
        if not status["running"]:
            sys.exit(1)
    
    elif args.command == "activate":
        ok, msg = activate_wechat()
        print(msg)
        if not ok:
            sys.exit(1)
    
    elif args.command == "search":
        ok, msg = search_contact(args.name)
        print(msg)
        if not ok:
            sys.exit(1)
    
    elif args.command == "send":
        ok, msg = send_message(args.to, args.msg)
        print(msg)
        if not ok:
            sys.exit(1)
    
    else:
        parser.print_help()
