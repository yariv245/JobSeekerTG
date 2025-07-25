import json


class GoozaliFullRequest():
    def __init__(self, base_url: str):
        self.view_id: str = "viwIOzPYaUGxlA0Jd"
        self.url = base_url.format(view_id=self.view_id)
        self.air_table_page_load_id: str = "pgl8w9irz5YClGmST"
        self.cookies: dict[str, str] = {}
        self.request_id: str = "reqGu8KVhmdHvq9Ut"
        self.expire: str = "2025-07-31T00:00:00.000Z"
        self.signature: str = "474f346b264a0503aaa4be298f49aa66494b31e5af72b35d5e46c40cd6ff3c5c"
        self.headers = self._generate_headers()
        self.params = self._generate_params()
        self.cookies = {}

    def _generate_params(self) -> dict[str, str]:
        access_policy = self._generate_access_policy()

        return {
            "stringifiedObjectParams": {
            "shouldUseNestedResponseFormat": "true"},
            "request_id": self.request_id,
            "accessPolicy": access_policy
        }

    def _generate_headers(self) -> str:
        return {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9,he-IL;q=0.8,he;q=0.7',
            'priority': 'u=1, i',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'x-airtable-accept-msgpack': 'true',
            'x-airtable-application-id': "appwewqLk7iUY4azc",
            'x-airtable-inter-service-client': 'webClient',
            'x-airtable-page-load-id': self.air_table_page_load_id,
            'x-early-prefetch': 'true',
            'x-requested-with': 'XMLHttpRequest',
            'x-time-zone': 'Asia/Jerusalem',
            'x-user-locale': 'en'
        }

    def _generate_access_policy(self) -> str:
        """
        Generates a JSON string for access policy.
        """
        access_policy = {
            "allowedActions": [
                {"modelClassName": "view", "modelIdSelector": self.view_id,
                 "action": "readSharedViewData"},
                {"modelClassName": "view", "modelIdSelector": self.view_id,
                 "action": "getMetadataForPrinting"},
                {"modelClassName": "view", "modelIdSelector": self.view_id,
                 "action": "readSignedAttachmentUrls"},
                {"modelClassName": "row", "modelIdSelector": f"rows *[displayedInView={self.view_id}]",
                 "action": "createDocumentPreviewSession"}
            ],
            "shareId": "shrQBuWjXd0YgPqV6",
            "applicationId": "appwewqLk7iUY4azc",
            "generationNumber": 0,
            "expires": self.expire,
            "signature": self.signature
        }
        # Convert to a JSON string
        return json.dumps(access_policy)
