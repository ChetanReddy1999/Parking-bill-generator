import numpy as np
import gradio as gr
import time
from src.upload_s3 import upload_image_to_s3
from PIL import Image
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv('app.env'), override=True)

def input_image(image):
    extracted_text, SrNo, entry_time, is_exit = upload_image_to_s3(image)
    if extracted_text is None:
        return gr.Warning("Number Plate Not Detected")
    
    if is_exit:
        print("Vehicle Number: ", extracted_text)
        gr.update(elem_id="dataframe", visible=False)
        return gr.Textbox(value=extracted_text)
    
    # Return the data to be displayed in Dataframe
    return [[SrNo, extracted_text, entry_time]]


with gr.Blocks() as demo:
    gr.Markdown(
        """
        <div style="text-align: center;">
            <h1 style="font-family:Cursive ;font-size: 3em; color: #FFFFFF; font-weight: bold; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);">PARKING BILL GENERATOR</h1>
        </div>
        """,
        elem_id="header"
    )

    with gr.Row():
        image = gr.Image(show_label=False, height=380, width=800, type="pil")
    with gr.Row():
        gr.Markdown("")
        submit = gr.Button(value="Submit", size='lg', variant='primary')
        gr.Markdown("")
    
    output_dataframe = gr.Dataframe(headers=["Sr No", "Vehicle Number", "Entry Time"], datatype=["number", "str", "str"], elem_id="dataframe")
    submit.click(fn=input_image, inputs=image, outputs=output_dataframe)
demo.launch()