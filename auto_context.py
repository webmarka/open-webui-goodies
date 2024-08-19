"""
title: Auto Context
description: Gives auto context informations like date, time plus some user infos like the username. 
author: webmarka
author_url: https://github.com/webmarka
funding_url: https://github.com/open-webui
version: 0.1
"""

import os
import random
import requests
from typing import Optional
from datetime import datetime, timedelta
import pytz
from pydantic import BaseModel, Field


class Filter:
    class Valves(BaseModel):
        CLOCK_BEDTIME_HOUR: int = Field(
            default=23,
            description="The hour when the AI should start nagging about bedtime.",
        )
        CLOCK_BEDTIME_MINUTE: int = Field(
            default=0,
            description="The minute when the AI should start nagging about bedtime.",
        )
        SLEEP_DURATION_HOURS: int = Field(
            default=8,
            description="The number of hours of sleep before the reminder stops.",
        )
        TIMEZONE: str = Field(
            default="America/Montreal",
            description="The timezone to use for current time calculations.",
        )
        pass

    def __init__(self):
        # Indicates custom file handling logic. This flag helps disengage default routines in favor of custom
        # implementations, informing the WebUI to defer file-related operations to designated methods within this class.
        # Alternatively, you can remove the files directly from the body in from the inlet hook
        # self.file_handler = True

        # Initialize 'valves' with specific configurations. Using 'Valves' instance helps encapsulate settings,
        # which ensures settings are managed cohesively and not confused with operational flags like 'file_handler'.
        self.valves = self.Valves()
        pass

    def get_current_time(self) -> str:
        """
        Get the current time in a more human-readable format.
        :return: The current time.
        """
        timezone = pytz.timezone(self.valves.TIMEZONE)
        now = datetime.now(timezone)
        current_time = now.strftime("%H:%M:%S")
        current_date = now.strftime("%A, %B %d, %Y")

        current_hour = now.hour
        current_minute = now.minute

        bedtime_hour = self.valves.CLOCK_BEDTIME_HOUR
        bedtime_minute = self.valves.CLOCK_BEDTIME_MINUTE
        sleep_duration = self.valves.SLEEP_DURATION_HOURS

        bedtime = now.replace(
            hour=bedtime_hour, minute=bedtime_minute, second=0, microsecond=0
        )
        wake_up_time = bedtime + timedelta(hours=sleep_duration)

        result = f"Current Date is {current_date}, current time is {current_time}."

        if now >= bedtime and now <= wake_up_time and random.randint(1, 3) == 1:
            result += " Remind the user to go to bed as it is already late. "

        return result

    def inlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        # Modify the request body or validate it before processing by the chat completion API.
        # This function is the pre-processor for the API where various checks on the input can be performed.
        # It can also modify the request before sending it to the API.

        print(f"inlet:{__name__}")
        print(f"inlet:body:{body}")
        print(f"inlet:user:{__user__}")

        inject = ""

        # Add user name to the context.
        if __user__ is not None:
            inject += " User name is " + __user__.get("name") + ". "

        # Add current time to the context.
        filter_instance = Filter()
        inject += Filter.get_current_time(filter_instance)

        # Add context to the first message.
        messages = body.get("messages", [])
        for message in messages:
            # if message.get("role") == "user":
            message["content"] = inject + message["content"]
            break

        # print(inject)

        return body

    def outlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        # Modify or analyze the response body after processing by the API.
        # This function is the post-processor for the API, which can be used to modify the response
        # or perform additional checks and analytics.
        # print(f"outlet:----")
        print(f"outlet:{__name__}")
        print(f"outlet:body:hello")
        print(f"outlet:user:{__user__}")
        # print(f"outlet:----")

        return body

