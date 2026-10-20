from ibm_watsonx_orchestrate.agent_builder.tools import tool
import requests

@tool()
def post_to_linkedin(post_text: str) -> dict:
    """
    Posts the given text directly to LinkedIn as a public post.
    """
    access_token = "AQUcmQkH-h7ro_C89BuYvLjHAJJb5ICJe1adweOPRv-IEK0vAegKXMmEm40Qiw0fRbtl_YTTAo1l07RUfTnk9UqV3NGdJD-MM7k4g2oCBn8YRHquAuhz9NhuhYiiv13bGhVOotck7f8_ETYJFgqknfnCmBK4ndZb07IFmKnEiZpunRzCM7DRezByU_ApFcxZ791q-eZtddzErvSEnTNfhHLf9eZcpb2RUL1btIGoGtSNTH74TdttmlADBogPYuMF3rvBKTumUFIes3hyhGNTOE2zPNMkT306U9UuR8fDeMDRMG2SiBU8rCKl9H_QDSbgDZAxPvS9CPbB1tmKEJZklMQG1b1d1g"
    author_urn   = "urn:li:person:p0CE8OuDw1"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "LinkedIn-Version": "202210",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }

    payload = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": post_text},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    response = requests.post(
        "https://api.linkedin.com/v2/ugcPosts",
        json=payload,
        headers=headers
    )

    if response.status_code == 201:
        post_id = response.headers.get("x-restli-id", "unknown")
        return {"status": "success", "post_id": post_id}

    return {"status": "error", "detail": response.text}

# Made with Bob
