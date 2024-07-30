# bingimg.py

# encoding:utf-8
import requests
import os
import plugins
from io import BytesIO
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger
from plugins import *

@plugins.register(
    name="bingImg",
    desire_priority=100,
    hidden=False,
    desc="A simple plugin that returns a bing image",
    version="0.1",
    author="lin1cc",
)

class BingImgPlugin(Plugin):
    def __init__(self):
        super().__init__()
        try:
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
            logger.info("[BingImgPlugin] inited.")
        except Exception as e:
            logger.warn("[BingImgPlugin] init failed, ignore.")
            raise e

    def on_handle_context(self, e_context: EventContext):
        if e_context["context"].type != ContextType.TEXT:
            return

        content = e_context["context"].content.strip()
        
        if content.startswith("美景图"):
            # 随机 数字 0-7
            random_num = str(random.randint(0, 7))
            # message = content.replace("美景图", "").strip()
            image_url = self.get_card_image_url(random_num)
            if image_url:
                image_data = self.download_image(image_url)
                if image_data:
                    reply = Reply(ReplyType.IMAGE, image_data)
                    e_context["reply"] = reply
                    e_context.action = EventAction.BREAK_PASS
                else:
                    reply = Reply(ReplyType.TEXT, "无法保存卡片图片，请稍后再试。")
                    e_context["reply"] = reply
            else:
                reply = Reply(ReplyType.TEXT, "无法生成卡片图片，请稍后再试。")
                e_context["reply"] = reply

    def get_help_text(self, **kwargs):
        help_text = "输入【美景图】 获得图片。"
        return help_text

    def get_card_image_url(self, count):
        api_url = "https://api.oioweb.cn/api/bing"
        try:
            response = requests.get(api_url)
            response.raise_for_status()

            #
            data = response.json()
            data_r = data.get("result")
            data_c = data_r[count]
            return data_c["url"]
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None
        except ValueError:
            logger.error("Failed to parse JSON response")
            return None
        
    def download_image(self, image_url):
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            image_data = BytesIO(response.content)
            logger.info("Image downloaded successfully")
            return image_data
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download image: {e}")
            return None
        
# 示例调用
if __name__ == "__main__":
    plugin = BingImgPlugin()
    print(plugin.get_card_image_url(3))
