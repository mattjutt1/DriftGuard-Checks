"""Simple test app to verify Gradio works"""
import gradio as gr

def greet(name):
    return f"Hello {name}! The PromptWizard training Space is setting up..."

demo = gr.Interface(
    fn=greet,
    inputs="text",
    outputs="text",
    title="PromptWizard Training Setup Test"
)

if __name__ == "__main__":
    demo.launch()