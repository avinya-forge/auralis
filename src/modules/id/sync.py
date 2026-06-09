import json


class ProfileSync:
    @staticmethod
    def export_profile(profile_data: dict) -> str:
        return json.dumps(profile_data, indent=4)

    @staticmethod
    def import_profile(json_data: str) -> dict:
        try:
            return json.loads(json_data)
        except json.JSONDecodeError:
            return {}
