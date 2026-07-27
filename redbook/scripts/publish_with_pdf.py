"""
Publish a Xiaohongshu note with PDF file attachment.

The xhs CLI doesn't expose the PDF attachment feature, so this script
directly uses the xhs_cli library to upload a PDF and attach it to the note.
"""
import json, mimetypes, os, sys, time
from pathlib import Path

# Use installed xiaohongshu-cli
from xhs_cli.commands._common import get_cookies
from xhs_cli.client_mixins import UPLOAD_HOST
from xhs_cli.constants import CREATOR_HOST
from xhs_cli.client import XhsClient

COOKIE_SOURCE = "auto"


def upload_file_raw(client: XhsClient, file_path: str, scene: str = "image") -> dict:
    """Upload a file and return {file_id, token}. Uses client's internal request."""
    count = 1
    data = client._creator_get("/api/media/v1/upload/web/permit", {
        "biz_name": "spectrum",
        "scene": scene,
        "file_count": count,
        "version": 1,
        "source": "web",
    })
    permit = data["uploadTempPermits"][0]
    file_id = permit["fileIds"][0]
    token = permit["token"]

    with open(file_path, "rb") as f:
        file_data = f.read()

    content_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
    url = f"{UPLOAD_HOST}/{file_id}"
    resp = client._request_with_retry("PUT", url, headers={
        "X-Cos-Security-Token": token,
        "Content-Type": content_type,
    }, content=file_data)
    if resp.status_code >= 400:
        raise RuntimeError(f"Upload failed: {resp.status_code}")
    return {"file_id": file_id, "token": token}


def create_note_with_pdf(
    client: XhsClient,
    title: str,
    desc: str,
    image_file_ids: list[str],
    pdf_file_id: str,
    pdf_name: str,
    pdf_size: int,
    topics: list[dict] | None = None,
    is_private: bool = False,
):
    """Create note with PDF attachment via the creator API."""
    images = [{"file_id": fid, "metadata": {"source": -1}} for fid in image_file_ids]

    business_binds = {
        "version": 1,
        "noteId": 0,
        "noteOrderBind": {},
        "notePostTiming": {"postTime": None},
        "noteCollectionBind": {"id": ""},
    }

    related_file = {
        "file_id": pdf_file_id,
        "name": pdf_name,
        "size": pdf_size,
        "type": "pdf",
    }

    payload = {
        "common": {
            "type": "normal",
            "title": title,
            "note_id": "",
            "desc": desc,
            "source": '{"type":"web","ids":"","extraInfo":"{\\"subType\\":\\"official\\"}"}',
            "business_binds": json.dumps(business_binds),
            "ats": [],
            "hash_tag": topics or [],
            "post_loc": {},
            "privacy_info": {"op_type": 1, "type": 1 if is_private else 0},
        },
        "image_info": {"images": images},
        "video_info": None,
        "related_file": related_file,
    }

    return client._main_api_post("/web_api/sns/v2/note", payload, {
        "origin": CREATOR_HOST,
        "referer": f"{CREATOR_HOST}/",
    })


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Publish note with PDF attachment")
    parser.add_argument("--title", required=True)
    parser.add_argument("--body", required=True)
    parser.add_argument("--pdf", required=True, help="Path to PDF file")
    parser.add_argument("--images", action="append", default=[], help="Image paths")
    parser.add_argument("--topic", action="append", default=[], help="Topic tags")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not args.images:
        print("ERROR: at least one --images required")
        sys.exit(1)

    # Get authenticated client
    browser_name, cookies = get_cookies(COOKIE_SOURCE)
    client = XhsClient(cookies)

    with client:
        # Upload PDF
        print(f"Uploading PDF: {args.pdf}")
        pdf_result = upload_file_raw(client, args.pdf, scene="file")
        pdf_file_id = pdf_result["file_id"]
        pdf_name = os.path.basename(args.pdf)
        pdf_size = os.path.getsize(args.pdf)
        print(f"  PDF uploaded: {pdf_file_id} ({pdf_size} bytes)")

        # Upload images
        image_ids = []
        for img_path in args.images:
            print(f"Uploading image: {os.path.basename(img_path)}")
            img_result = upload_file_raw(client, img_path, scene="image")
            image_ids.append(img_result["file_id"])
            print(f"  Image uploaded: {img_result['file_id']}")

        # Build topics
        topics = [{"id": "", "name": t, "type": "topic"} for t in args.topic]

        # Create note
        print(f"\nPublishing note...")
        result = create_note_with_pdf(
            client, args.title, args.body,
            image_ids, pdf_file_id, pdf_name, pdf_size, topics,
        )

        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            note_id = result.get("data", {}).get("id", result.get("id", ""))
            if note_id:
                print(f"Done! ID: {note_id}")
                print(f"URL: https://www.xiaohongshu.com/explore/{note_id}")
            else:
                print(f"Response: {json.dumps(result, ensure_ascii=False)[:500]}")


if __name__ == "__main__":
    main()
