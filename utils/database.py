"""database controller"""

import logging
import pymongo

from sys import stderr
from typing import Dict, Union, List
from bson import ObjectId

from utils.config import DockerConfig
from cogs.data.collection import ASSET_COLLECTION, CHANNEL_COLLECTION

LOG = logging.getLogger(__name__)
CONFIG = DockerConfig("config.ini")

DBCONFIG = {
    "url":     CONFIG.get_var("MONGODB", "URL"),
    "database": CONFIG.get_var("MONGODB", "DB_NAME")
}

class MongoDriver:
    """
        This class contains some basics MongoDB features
        
        It represents a connection to a database
    """

    def __init__(self):
        self.client = pymongo.MongoClient(
            DBCONFIG["url"]
        )
        
        self.database = None
        self.collection = None

        self.set_database(DBCONFIG["database"])
        LOG.info("[+] A connection to the database has been created")

    def init_collection(self, name: str, schema: dict):
        """
            Add a collection to the database
        """

        try:
            self.database.create_collection(
                name,
                validator=schema
            )
        except Exception as error:
            print(error, file=stderr)
    
    def init_collections(self, name: str, collection: dict):
        """
            Method prototype
        """

        raise NotImplementedError("Not implemented")

    def set_database(self, name: str) -> "MongoDriver":
        """
            Switching Mongo database
        """

        self.database = self.client[name]

        return self

class TwUtilsDB(MongoDriver):
    """
        This class manages the connection and requests with MongoDB
        for Teeworlds Utilities
    """

    def __init__(self):
        super().__init__()

        self.init_collections()
    
    def init_collections(self):
        """
            Initializes the collections schemas
        """

        # twutils database
        self.set_database("twutils")

        # twutils collections
        self.init_collection("discordAssets", ASSET_COLLECTION)
        self.database["discordAssets"].create_index(
            [
                ("guildID", pymongo.ASCENDING),
                ("checksum", pymongo.ASCENDING)
            ],
                unique=True
        )

        self.init_collection("discordChannels", CHANNEL_COLLECTION)
        self.database["discordChannels"].create_index(
            [
                ("guildID", pymongo.ASCENDING)
            ],
                unique=True
        )
    
    def duplicate(
        self,
        checksum: str,
        guild_id: str
    ) -> Union[Dict, None]:
        """
            Checks if the asset hash already exist
            in the collection (accepted or not)
        """

        res = self.database["discordAssets"].find_one(
            {
                "checksum": checksum,
                "guildID": guild_id
            }
        )

        return res

    def find_by_checksum(
        self,
        checksum: str,
    ) -> Union[Dict, None]:
        """
            Returns assets informations by his id
        """

        ret = self.database["discordAssets"].find_one(
            {
                "checksum": checksum
            }
        )

        return ret

    def add_to_queue(self, fields: dict) -> Union[Dict, None]:
        """
            Adds asset informations to the queue
        """

        ret = None

        try:
            ret = self.database["discordAssets"].insert_one(fields)
        except Exception as error:
            print(error, file=stderr)

        return ret

    def accept(self, _id: str, guild_id: str) -> Union[Dict, None]:
        """
            Accept an asset for a specific Discord guild
        """

        try:
            ret = self.database["discordAssets"].find_one_and_update(
                {
                    "_id": ObjectId(_id),
                    "guildID": guild_id,
                    "accepted": False
                }, {
                    "$set": {
                        "accepted": True
                    }
                },
                return_document=pymongo.ReturnDocument.AFTER
            )
        except:
            return None

        return ret
        
    def get_asset_by_id(self, _id: str, guild_id: str) -> Union[Dict, None]:
        """
            Return an asset document with his _id
        """

        try:
            ret = self.database["discordAssets"].find_one(
                {
                    "_id": ObjectId(_id),
                    "guildID": guild_id
                }
            )
        except Exception:
            return None

        return ret

    def get_accepted_asset_by_id(self, _id: str, guild_id: str) -> Union[Dict, None]:
        """
            Return an asset document with his _id
        """

        try:
            ret = self.database["discordAssets"].find_one(
                {
                    "_id": ObjectId(_id),
                    "guildID": guild_id,
                    "accepted": True
                }
            )
        except Exception:
            return None

        return ret
    
    def get_queue(self, guild_id: str) -> Union[List, None]:
        """
            Return every assets in the queue
        """

        try:
            ret = self.database["discordAssets"].find(
                {
                    "guildID": guild_id,
                    "accepted": False
                }
            ).sort("createdAt", -1)
        except Exception:
            return None

        return list(ret)
    
    def get_guild_asset_by_id(self, _id: str, guild_id: str) -> Union[Dict, None]:
        """
            Return an asset document with his _id
        """

        try:
            ret = self.database["discordAssets"].find_one(
                {
                    "_id": ObjectId(_id),
                    "guildID": guild_id
                }
            )
        except Exception:
            return None

        return ret

    def link_msg_id(
        self,
        _id: ObjectId,
        msg_id: str,
        channel_id: str
    ) -> Union[Dict, None]:
        """
            Archive an asset for a specific Discord guild
        """

        try:
            ret = self.database["discordAssets"].find_one_and_update(
                {
                    "_id": _id
                }, {
                    "$set": {
                        "discord_msg_id": msg_id,
                        "discord_channel_id": channel_id
                    }
                },
                return_document=pymongo.ReturnDocument.AFTER
            )
        except Exception as error:
            print(error, file=stderr)
            return None

        return ret
    
    def remove_asset_by_id(self, _id: str, guild_id: str) -> Union[Dict, None]:
        """
            Remove asset document for a specific Discord guild
        """

        try:
            ret = self.database["discordAssets"].find_one_and_delete(
                {
                    "_id": ObjectId(_id),
                    "guildID": guild_id
                }, 
                return_document=pymongo.ReturnDocument.BEFORE
            )
        except:
            return None

        return ret

    def add_guild(self, fields: dict) -> Union[Dict, None]:
        """
            create a document for the channel collection
        """

        ret = None

        try:
            ret = self.database["discordChannels"].insert_one(fields)
        except Exception as error:
            print(error, file=stderr)

        return ret

    def set_channel(
        self,
        guild_id: str,
        channel_id: str,
        category: str
    ) -> Union[Dict, None]:
        """
            Link a category with a channel
        """

        try:
            ret = self.database["discordChannels"].find_one_and_update(
                {
                    "guildID": guild_id
                }, {
                    "$set": {
                        category: channel_id
                    }
                },
                return_document=pymongo.ReturnDocument.AFTER
            )
        except Exception:
            return None

        return ret

    def get_channels(
        self,
        guild_id: str,
        category: str
    ) -> Union[Dict, None]:
        """
            Returns a channel ID for category with a guild ID + category name
        """

        try:
            ret = self.database["discordChannels"].find_one(
                {
                    "guildID": guild_id,
                    category: {
                        "$exists": True
                    }
                },
            )
        except Exception:
            return None

        return ret
    
    def get_assets_contain_name(
        self,
        guild_id: str,
        name: str
    ) -> Union[List, None]:
        """
            Returns every asset containing the subtring [name] in their name
        """

        try:
            ret = self.database["discordAssets"].find(
                {
                    "guildID": guild_id,
                    "assetName": {
                        "$regex": name
                    },
                    "accepted": True
                }
            ).sort("createdAt", -1)
        except Exception as error:
            print(error, file=stderr)
            return None

        return list(ret)

    def get_assets_by_type(
        self,
        guild_id: str,
        _type: str
    ) -> Union[List, None]:
        """
            Returns every asset of type [_type]
        """

        try:
            ret = self.database["discordAssets"].find(
                {
                    "guildID": guild_id,
                    "type": _type,
                    "accepted": True
                }
            ).sort("createdAt", -1)
        except Exception:
            return None

        return list(ret)
    