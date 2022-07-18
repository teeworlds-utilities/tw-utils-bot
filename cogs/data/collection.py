"""collection module"""

from cogs.data.asset import ASSET_TYPE

ASSET_COLLECTION = {
    "$jsonSchema": {
        "required": [
            "assetName",
            "type",
            "path",
            "checksum",
            "guildID",
            "authorName",
            "authorID",
            "accepted"
        ],
        "properties": {
            "assetName": {
                "bsonType": "string",
                "description": "represents the asset name, must be a string and required"
            },
            "type": {
                "bsonType": "string",
                "description": "represents the asset type, must be a string and required"
            },
            "path": {
                "bsonType": "string",
                "description": "represents the file path, must be a string and required"
            },
            "createdAt": {
                "bsonType": "date",
                "description": "represents the asset checksum, must be a date"
            },
            "checksum": {
                "bsonType": "string",
                "description": "represents the asset checksum, must be a string, required"
            },
            "guildID": {
                "bsonType": "string",
                "description": "represents the asset checksum, must be a string, required"
            },
            "authorID": {
                "bsonType": "string",
                "description": "represents the asset checksum, must be a string and required"
            },
            "authorName": {
                "bsonType": "string",
                "description": "represents the asset checksum, must be a string and required"
            },
            "accepted": {
                "bsonType": "bool",
                "description": "represents the asset state, must be a bool"
            },
            "discord_msg_id": {
                "bsonType": "string",
                "description": "represents the asset Discord linked message, must be a string"
            },
            "discord_channel_id": {
                "bsonType": "string",
                "description": "represents the asset Discord linked channel, must be a string"
            }
        }
    }
}

def channel_properties():
    """
        Generates properties for the channel collection
    """

    ret = {}

    for name in ASSET_TYPE.keys():
        ret[name] = {
            "bsonType": "string",
            "description": "represents a discord channel, must be a string"
        }

    return ret

CHANNEL_COLLECTION = {
    "$jsonSchema": {
        "required": [
            "guildID"
        ],
        "properties": {
            "guildID": {
                "bsonType": "string",
                "description": "represents a Discord guild id, must be a string and required"
            },
            **channel_properties()
        }
    }
}
