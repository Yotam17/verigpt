from pathlib import Path
from langchain.prompts import PromptTemplate

def get_prompt(prompt_fn: str, params: dict, base_dir: str = "prompts") -> str:
    """
    Load a prompt template from prompts/{prompt_fn}.md
    and format it with provided params.

    :param prompt_fn: filename (without .md)
    :param params: dict of values to inject
    :param base_dir: base folder for prompt files
    :return: formatted string
    """
    file_path = Path(base_dir) / f"{prompt_fn}.md"
    if not file_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        prompt_template = f.read()

    template = PromptTemplate(
        input_variables=list(params.keys()),
        template=prompt_template,
    )

    try:
        return template.format(**params)
    except KeyError as e:
        raise KeyError(f"Missing parameter for prompt: {e}")
