"""
Title: Meeting Minutes Extraction and Formatting Tool

Description:
This tool is designed to extract meeting minutes from a transcript using OpenAI's API and convert the extracted data into a formatted Markdown document. It allows users to input a meeting transcript, select an OpenAI model, and generate well-structured meeting minutes. The tool also provides functionality to download the minutes as a plain text file.

Features:
- Extracts meeting minutes from a given transcript using OpenAI's API.
- Converts the extracted data into a Markdown format for easy reading.
- Allows downloading of the meeting minutes as a plain text file.
- Supports various OpenAI models for flexible and accurate text processing.

Usage:
1. Enter the meeting transcript into the provided text area.
2. Select the desired OpenAI model.
3. Click 'Create Minutes' to process the transcript and generate minutes.
4. View the formatted meeting minutes and download them if needed.

Author: @CivilEngineerUK
Date: 05-12-2023
"""

#!pip install streamlit openai instructorS

import base64
import json
from pydantic import BaseModel, Field
from instructor import OpenAISchema
from typing import List, Optional, Dict, Any
from datetime import datetime
import streamlit as st
import openai
from enum import Enum


__author__ = 'Mike Rustell'
__email__ = 'mike@inframatic.ai'
__github__ = 'CivilEngineerUK'



test_data = """Meeting of CTAS County Commission-Transcript of Dialogue

Chairman Wormsley (at the proper time and place, after taking the chair and striking the gavel on the table): This meeting of the CTAS County Commission will come to order. Clerk please call the role. (Ensure that a majority of the members are present.)

Chairman Wormsley: Each of you has received the agenda. I will entertain a motion that the agenda be approved.

Commissioner Brown: So moved.

Commissioner Hobbs: Seconded

Chairman Wormsley: It has been moved and seconded that the agenda be approved as received by the members. All those in favor signify by saying "Aye"?...Opposed by saying "No"?...The agenda is approved. You have received a copy of the minutes of the last meeting. Are there any corrections or additions to the meeting?

Commissioner McCroskey: Mister Chairman, my name has been omitted from the Special Committee on Indigent Care.

Chairman Wormsley: Thank you. If there are no objections, the minutes will be corrected to include the name of Commissioner McCroskey. Will the clerk please make this correction. Any further corrections? Seeing none, without objection the minutes will stand approved as read. (This is sort of a short cut way that is commonly used for approval of minutes and/or the agenda rather than requiring a motion and second.)

Chairman Wormsley: Commissioner Adkins, the first item on the agenda is yours.

Commissioner Adkins: Mister Chairman, I would like to make a motion to approve the resolution taking money from the Data Processing Reserve Account in the County Clerk's office and moving it to the equipment line to purchase a laptop computer.

Commissioner Carmical: I second the motion.

Chairman Wormsley: This resolution has a motion and second. Will the clerk please take the vote.

Chairman Wormsley: The resolution passes. We will now take up old business. At our last meeting, Commissioner McKee, your motion to sell property near the airport was deferred to this meeting. You are recognized.

Commissioner McKee: I move to withdraw that motion.

Chairman Wormsley: Commissioner McKee has moved to withdraw his motion to sell property near the airport. Seeing no objection, this motion is withdrawn. The next item on the agenda is Commissioner Rodgers'.

Commissioner Rodgers: I move adopton of the resolution previously provided to each of you to increase the state match local litigation tax in circuit, chancery, and criminal courts to the maximum amounts permissible. This resolution calls for the increases to go to the general fund.

Chairman Wormsley: Commissioner Duckett

Commissioner Duckett: The sheriff is opposed to this increase.

Chairman Wormsley: Commissioner, you are out of order because this motion has not been seconded as needed before the floor is open for discussion or debate. Discussion will begin after we have a second. Is there a second?

Commissioner Reinhart: For purposes of discussion, I second the motion.

Chairman Wormsley: Commissioner Rodgers is recognized.

Commissioner Rodgers: (Speaks about the data on collections, handing out all sorts of numerical figures regarding the litigation tax, and the county's need for additional revenue.)

Chairman Wormsley: Commissioner Duckett

Commissioner Duckett: I move an amendment to the motion to require 25 percent of the proceeds from the increase in the tax on criminal cases go to fund the sheriff's department.

Chairman Wormsley: Commissioner Malone

Commissioner Malone: I second the amendment.

Chairman Wormsley: A motion has been made and seconded to amend the motion to increase the state match local litigation taxes to the maximum amounts to require 25 percent of the proceeds from the increase in the tax on criminal cases in courts of record going to fund the sheriff's department. Any discussion? Will all those in favor please raise your hand? All those opposed please raise your hand. The amendment carries 17-2. We are now on the motion as amended. Any further discussion?

Commissioner Headrick: Does this require a two-thirds vote?

Chairman Wormsley: Will the county attorney answer that question?

County Attorney Fults: Since these are only courts of record, a majority vote will pass it. The two-thirds requirement is for the general sessions taxes.

Chairman Wormsley: Other questions or discussion? Commissioner Adams.

Commissioner Adams: Move for a roll call vote.

Commissioner Crenshaw: Second

Chairman Wormsley: The motion has been made and seconded that the state match local litigation taxes be increased to the maximum amounts allowed by law with 25 percent of the proceeds from the increase in the tax on criminal cases in courts of record going to fund the sheriff's department. Will all those in favor please vote as the clerk calls your name, those in favor vote "aye," those against vote "no." Nine votes for, nine votes against, one not voting. The increase fails. We are now on new business. Commissioner Adkins, the first item on the agenda is yours.

Commissioner Adkins: Each of you has previously received a copy of a resolution to increase the wheel tax by $10 to make up the state cut in education funding. I move adoption of this resolution.

Chairman Wormsley: Commissioner Thompson

Commissioner Thompson: I second.

Chairman Wormsley: It has been properly moved and seconded that a resolution increasing the wheel tax by $10 to make up the state cut in education funding be passed. Any discussion? (At this point numerous county commissioners speak for and against increasing the wheel tax and making up the education cuts. This is the first time this resolution is under consideration.) Commissioner Hayes is recognized.

Commissioner Hayes: I move previous question.

Commisioner Crenshaw: Second.

Chairman Wormsley: Previous question has been moved and seconded. As you know, a motion for previous question, if passed by a two-thirds vote, will cut off further debate and require us to vote yes or no on the resolution before us. You should vote for this motion if you wish to cut off further debate of the wheel tax increase at this point. Will all those in favor of previous question please raise your hand? Will all those against please raise your hand? The vote is 17-2. Previous question passes. We are now on the motion to increase the wheel tax by $10 to make up the state cut in education funding. Will all those in favor please raise your hand? Will all those against please raise your hand? The vote is 17-2. This increase passes on first passage. Is there any other new business? Since no member is seeking recognition, are there announcements? Commissioner Hailey.

Commissioner Hailey: There will be a meeting of the Budget Committee to look at solid waste funding recommendations on Tuesday, July 16 at noon here in this room.

Chairman Wormsley: Any other announcements? The next meeting of this body will be Monday, August 19 at 7 p.m., here in this room. Commissioner Carmical.

Commissioner Carmical: There will be a chili supper at County Elementary School on August 16 at 6:30 p.m. Everyone is invited.

Chairman Wormsley: Commissioner Austin.

Commissioner Austin: Move adjournment.

Commissioner Garland: Second.

Chairman Wormsley: Without objection, the meeting will stand adjourned.
"""


class Participant(BaseModel):
    name: str = Field(..., description="The full name of the meeting participant.")
    role: Optional[str] = Field(None, description="The role or title of the participant within the meeting.")

class AgendaItem(BaseModel):
    title: str = Field(..., description="The title or topic of the agenda item.")
    description: Optional[str] = Field(None, description="A brief description of the agenda item.")

class DiscussionPoint(BaseModel):
    speaker: str = Field(..., description="The name of the person speaking on this point.")
    content: str = Field(..., description="The content or substance of the discussion point.")

class Motion(BaseModel):
    proposed_by: str = Field(..., description="The name of the person who proposed the motion.")
    seconded_by: str = Field(..., description="The name of the person who seconded the motion.")
    description: str = Field(..., description="A detailed description of what the motion entails.")
    result: Optional[str] = Field(None, description="The result of the motion, e.g., passed, failed, tabled.")

class PriorityEnum(str, Enum):
    high = "High"
    medium = "Medium"
    low = "Low"

class Subtask(BaseModel):
    """Subtask derived from the transcript."""
    id: int
    name: str

class Ticket(BaseModel):
    """Ticket representing an action item derived from the transcript."""
    id: int
    name: str
    description: str
    priority: PriorityEnum
    assignees: List[str] = Field(default_factory=list)
    subtasks: Optional[List[Subtask]] = None
    dependencies: Optional[List[int]] = None

class ActionItems(BaseModel):
    """Collection of action items extracted from the transcript."""
    items: List[Ticket]

class MeetingMinutes(OpenAISchema):  # Assuming OpenAISchema is a BaseModel
    meeting_title: str = Field(..., description="The official title of the meeting.")
    date: datetime = Field(..., description="The date and time when the meeting took place.")
    location: str = Field(..., description="The physical or virtual location of the meeting.")
    chairperson: str = Field(..., description="The name of the individual chairing the meeting.")
    participants: List[Participant] = Field(..., description="A list of participants who attended the meeting.")
    agenda: List[AgendaItem] = Field(..., description="A list of agenda items discussed during the meeting.")
    discussions: List[DiscussionPoint] = Field(..., description="A list of discussion points covered in the meeting.")
    motions: Optional[List[Motion]] = Field(None, description="A list of motions proposed and voted on during the meeting.")
    actions: Optional[ActionItems] = Field(None, description="A list of action items derived from the meeting transcript.")
    conclusions: Optional[str] = Field(None, description="Conclusions or summary of the meeting outcomes.")
    next_meeting_date: Optional[datetime] = Field(None, description="The scheduled date and time for the next meeting.")
    next_meeting_agenda: Optional[str] = Field(None, description="A preliminary agenda for the next meeting.")


def generate_action_items(transcript: str, model: str) -> MeetingMinutes:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Extract meeting minutes from the following transcript:"},
            {"role": "user", "content": transcript},
        ],
        functions=[MeetingMinutes.openai_schema],
        function_call="auto",
        temperature=0.0
    )
    return response

def dict_to_markdown(data: Dict[str, Any]) -> str:
    markdown_output = []

    def process_field(field_name, value):
        if isinstance(value, list):
            markdown_output.append(f"### {field_name.replace('_', ' ').capitalize()}\n")
            for item in value:
                if isinstance(item, dict):
                    process_dict(item)
                else:
                    markdown_output.append(f"- {item}\n")
        elif isinstance(value, dict):
            process_dict(value)
        else:
            markdown_output.append(f"**{field_name.replace('_', ' ').capitalize()}**: {value}\n")

    def process_dict(sub_data: Dict[str, Any]):
        for field_name, field_value in sub_data.items():
            if field_value is not None:
                process_field(field_name, field_value)

    process_dict(data)
    return ''.join(markdown_output)


def download_link(object_to_download, download_filename, download_link_text):
    """
    Generates a link to download the given object_to_download.
    """
    try:
        b64 = base64.b64encode(object_to_download.encode()).decode()
        return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'
    except Exception as e:
        return str(e)

def serialize_completion(completion):
    return {
        "id": completion.id,
        "choices": [
            {
                "finish_reason": choice.finish_reason,
                "index": choice.index,
                "message": {
                    "content": choice.message.content,
                    "role": choice.message.role,
                    "function_call": {
                        "arguments": json.loads(
                            choice.message.function_call.arguments) if choice.message.function_call and choice.message.function_call.arguments else None,
                        "name": choice.message.function_call.name
                    } if choice.message and choice.message.function_call else None
                } if choice.message else None
            } for choice in completion.choices
        ],
        "created": completion.created,
        "model": completion.model,
        "object": completion.object,
        "system_fingerprint": completion.system_fingerprint,
        "usage": {
            "completion_tokens": completion.usage.completion_tokens,
            "prompt_tokens": completion.usage.prompt_tokens,
            "total_tokens": completion.usage.total_tokens
        }
    }

# App starts here
st.title("Meeting Minutes Extractor")
st.markdown(
    """
    Developed by [CivilEngineerUK](https://github.com/CivilEngineerUK)   [![GitHub Repo](https://img.shields.io/github/stars/CivilEngineerUK/meeting_mins_app?style=social)](https://github.com/CivilEngineerUK/meeting_mins_app)
    """,
    unsafe_allow_html=True,
)
st.write("This app extracts meeting minutes from a meeting transcript using OpenAI's API into a"
         "schema and allows you to download as markdown.")

# Checkbox to enter OpenAI API key
if st.checkbox("Enter OpenAI API Key", value=False, key="enter_api_key", help="Enter your OpenAI API key."):
    st.session_state["api_key"] = st.text_input("OpenAI API Key", placeholder="Enter your OpenAI API key here.")

if "api_key" in st.session_state:
    client = openai.OpenAI(api_key=st.session_state["api_key"])

    # Show OpenAI schema checkbox
    if st.checkbox("Show OpenAI schema", value=False, key="show_schema", help="Show the OpenAI schema for this function."):
        st.json(MeetingMinutes.openai_schema)

    # Meeting transcript input
    # allow test data
    if st.checkbox("Use test data", value=False, key="use_test_data", help="Use test data for demonstration purposes. Found at: https://www.ctas.tennessee.edu/eli/sample-meeting-transcript"):
        example_text = test_data
    else:
        example_text = ""
    transcript = st.text_area("Enter Meeting Transcript:", value=example_text, height=300, placeholder=test_data)

    # OpenAI model selection
    model = st.selectbox("Select OpenAI Model:", ["gpt-3.5-turbo", "gpt-4-1106-preview", "gpt-3.5-turbo-1106"])

    # Process and generate meeting minutes
    if st.button("Create Minutes"):
        with st.spinner("Generating meeting minutes..."):
            if transcript:
                try:
                    action_items = generate_action_items(transcript, model)
                    st.session_state['raw_response'] = serialize_completion(action_items)
                except Exception as e:
                    st.error(f"An error occurred while generating action items: {e}")
            else:
                st.warning("Please enter a transcript to extract action items from.")


    if 'raw_response' in st.session_state:
        if st.checkbox("Show raw response as JSON", value=False, key="show_raw_response"):
            st.subheader("Raw Response (JSON):")
            st.json(st.session_state['raw_response'])
        try:
            # Extracting the specific part of the response
            meeting_minutes_data = st.session_state['raw_response']["choices"][0]["message"]["function_call"]["arguments"]

            if isinstance(meeting_minutes_data, dict):
                markdown_document = dict_to_markdown(meeting_minutes_data)
                st.subheader("Meeting Minutes:")
                st.markdown(markdown_document, unsafe_allow_html=True)
                st.markdown(download_link(markdown_document, "meeting_minutes.txt", "Download Meeting Minutes as TXT"),
                            unsafe_allow_html=True)
            else:
                st.error("Invalid response format for meeting minutes.")
        except Exception as e:
            st.error(f"An error occurred while processing the response: {e}")