# July 23 MCP + Claude Code Work in Progress

Testing out MCP with [Claude Code](https://www.anthropic.com/claude-code). Also, I use uv. To install uv use:

```
pip install uv
```

In one terminal, run:

```
uv run tap_mcp_server.py stdio
```

In the other terminal, run:

```
claude mcp add tap-schema-server -- uv run tap_mcp_server.py
```

Then use Claude Code, provide it a TAP URL, and ask it about the TAP database.

Since I'm currently testing on LSST DP1. You should have your LSST token as an `ASTRO_DATABASE_TOKEN` env var.

Example prompt for Claude:
```
Make a CMD and color-color plot for Abell 360  covered by DP1 at RA=37.865deg, DEC=6.982deg, range_deg = 0.1.

Use the MCP tool and https://data.lsst.cloud/api/tap to figure out the column names and tables you need.

When you actually get to querying LSST, use PyVO with url.replace("https://", f"https://x-oauth-basic:{os.environ["ASTRO_DATABASE_TOKEN"]}@").
```
---

# For Custom GPTs
## ChatAstro - Chatting with TAP servers

At the moment, this repo contains work in progress towards a chatbot for every TAP server.

While that is being built, you can try the public version of ChatGaia here: [https://chatgpt.com/g/g-aYZOjK5zy-chatgaia](https://chatgpt.com/g/g-aYZOjK5zy-chatgaia)

 **ChatGaia** is a custom GPT designed to interface with the ESA Gaia Archive. ChatGaia enables users to ask astrophysics research questions in natural language; it then translates these into ADQL queries, provides download URLs for the data, and can assist in analyzing the results once the data is uploaded by the user. 
 
 The public-facing version of ChatGaia (released Nov 2023) was built using OpenAI's Custom GPT feature.

To make a custom GPT you need:

1. **A System Prompt:** This instructs the GPT on its persona, tasks, response format, and specific rules to follow.

2. **Uploaded Knowledge Files:** These files provide the GPT with domain-specific information it can retrieve and use when generating responses using retrieval augmented generation (the GPT only sees the parts of the file most relevant to the user query). For ChatGaia, I uploaded the Gaia DR3 schema.

3. **A ChatGPT Plus Subscription**
  
### The Prompt (`chatgaia_prompt.txt`)

This prompt instructs the GPT to translate research questions into ADQL queries for the Gaia Archive. It also contains Instruction to use the schema file: e.g. `Before answering any query, check column_names.txt. You MUST search column_names.txt before writing any query.`

It also instructs the GPT to formatting for ADQL queries and download URLs and contains an ADQL "cheat sheet" and Python plotting preferences.

Furthermore, it provides some example queries.

  

#### **The Gaia Schema File (`gaia_schema.txt`) for RAG**

 `gaia_schema.txt` is a text file containing a structured representation of the Gaia Archive's database schema. This includes:

* Table names and descriptions (e.g., `gaiadr3.gaia_source`, `gaiadr3.astrophysical_parameters`).

* A list of its columns including descriptions, units, and datatypes

###### How it was generated:

The schema was generated using an older script similar to `llm_schema.py` provided in this repository.

The newer `llm_schema.py` in this rep uses the `pyvo` library to connect to a TAP service URL (e.g., Gaia's TAP service: `https://gea.esac.esa.int/tap-server/tap`).

The TAP urls expose their schema through a structured XML format,  like NOIRLab's Data Lab TAP service tables page (`https://datalab.noirlab.edu/tap/tables`) or the Chandra X-ray Center TAP service (`https://cda.harvard.edu/cxctap/tables`). The script parses this information and formats it into a text file suitable for LLM consumption.

The `schema.txt` file is uploaded directly into the "Knowledge" section of the Custom GPT configuration panel.

When a user asks a question, ChatGPT **automatically performs Retrieval Augmented Generation (RAG)**. It searches the content of `schema.txt` to find relevant table and column names, their descriptions, and other metadata to construct accurate ADQL queries.

### Final Thoughts
Once a custom GPT is created, you can share it publicaly, even to those who do not have ChatGPT Plus. 

The user interacts with the GPT by: asking for data, copying the generated query URL, pasting it in the browser, then they can upload the downloaded data and ask for plotting or analysis.

They have to copy the URL for two silly reasons: 1) ChatGPT does not allow API's to download data to its local environment and 2) long ChatGPT generated links are usually not clickable for some reason. (Update: actually this second part seems to have been solved!)

I have a plan for making a dedicated webapp that allows users to chat with any TAP service like ChatGaia, but this is limited by the free time I can spend on it! However, this will only be for generating queries, downloading and analyzing data on the webapp would require a large compute load. So something like a ChatAstro hosted on a science platform would be the ultimate end goal.