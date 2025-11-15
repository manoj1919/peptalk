

# **Project "PEP-talk": A Vertical-Slice Implementation Blueprint**

## **Executive Summary: The Vertical Slice Strategy**

The "PEP-talk" project brief outlines an ambitious and high-value platform for transforming dense, static texts into interactive learning environments. The proposed architecture, centered on a domain-agnostic engine, is sound. The immediate goal is the development of an "end-to-end vertical slice" proof of concept (POC).

This blueprint provides a comprehensive, step-by-step implementation plan for this vertical-slice POC. The strategy is to demonstrate *all four* core features of the platform:

1. **The "Living Text"** (RAG-based chat)  
2. **Dynamic Examples** (Context-grounded synthetic data)  
3. **Real-World Connections** (File wrapper argument retrieval)  
4. **AI Mock Evaluator** (LLM-as-a-Judge)

This implementation will be strictly scoped to a narrow but complex domain: **MPEP Chapters 2141-2145** (Obviousness under 35 U.S.C. 103). This "vertical slice" approach is designed to validate the entire architecture and de-risk future development by proving that the most complex, interconnected features can function as a cohesive system before scaling horizontally to the entire MPEP or other domains.

This document provides the technical instructions for (1) the data-ingestion pipeline, (2) the backend AI architecture, (3) the frontend UI construction, and (4) the implementation of the advanced AI features required for the POC.

## **Part 1: The Data Foundation: A Structure-Aware MPEP Ingestion Pipeline**

The success of any Retrieval-Augmented Generation (RAG) system is determined by the quality of its data ingestion pipeline. The user's request to "preserve styling" is a critical requirement, which, in this context, translates to preserving the *semantic structure* of the legal text. This structure is essential for accurate, context-aware retrieval.

### **1.1 Sourcing the "Ground Truth" (MPEP 2141-2145)**

The integrity of the system demands the use of official, canonical source material. The ingestion pipeline for the POC must target the official USPTO HTML versions of the MPEP, not PDF versions. The HTML format contains the necessary semantic tags (headings, lists, etc.) that define the document's hierarchy, whereas a PDF would require an unnecessary and often error-prone Optical Character Recognition (OCR) step.

For this specific POC, the pipeline should be configured to scrape the following pages:

* MPEP § 2141: *Prima Facie* Case for Obviousness  
* MPEP § 2143: Obviousness Rationales  
* MPEP § 2144: Supporting a Rejection  
* MPEP § 2145: Rebuttal Arguments

### **1.2 The "Preserve Styling" Solution: A Two-Step HTML-to-Markdown Pipeline**

A common failure mode in web scraping for RAG is using a simple .get\_text() function (common with libraries like BeautifulSoup), which strips all semantic information and results in an unstructured "blob" of text. This destroys the context.

The LLM does not require literal CSS styling, but it fundamentally relies on the *semantic structure* encoded by HTML tags (\<h1\>, \<h2\>, \<ul\>, \<strong\>). The optimal solution is to convert this structured HTML into Markdown, which is a lightweight format that preserves the document's hierarchy.

The step-by-step implementation is as follows:

1. **Scrape HTML Content:** Utilize Python libraries requests to fetch the MPEP pages and BeautifulSoup to parse the HTML. Instead of extracting text, the scraper should identify the main content div of the MPEP page and extract its complete *inner HTML*.  
2. **Convert to Markdown:** Employ a Python library such as html-to-markdown or markdownify to process the extracted HTML. This will intelligently transform the HTML tags into their Markdown equivalents (e.g., \<h2\>2141...\</h2\>\<p\>text\</p\> becomes \#\# 2141...\\n\\ntext).  
3. **Result:** The output of this stage will be a clean mpep\_2141-2145.md file. This file preserves all section headings, sub-headings, lists, and emphasis, providing a perfect, high-fidelity input for the next stage: chunking.

### **1.3 Advanced Chunking for Legal Text: A Hierarchical Approach**

With a structured Markdown file, the next step is to "chunk" the text for the vector database. The choice of chunking strategy is arguably the most important architectural decision for this RAG system.

Basic chunking strategies are ill-suited for the MPEP:

* **Fixed-Size Chunking** is the worst option. It will arbitrarily slice legal rules and definitions in half, destroying their meaning and leading to incoherent, incorrect retrievals.  
* **Recursive Character Splitting** is a common default, splitting on \\n\\n, then \\n, etc. While an improvement, it still lacks an understanding of the *logical* and *numbered* hierarchy of the MPEP. It might group unrelated sections or split a large, cohesive section.  
* **Semantic Chunking** splits by topic similarity. This is overly complex and potentially counter-productive for a legal manual where adjacent sections (e.g., "Teaching Away" vs. "Unexpected Results") are intentionally distinct topics that must not be merged.

The *correct* approach is **Structure-Aware Chunking** that leverages the Markdown headers we just preserved. The LangChain framework provides the ideal tool for this: MarkdownHeaderTextSplitter. This splitter is designed to create one document chunk per header section.

**Step-by-Step Implementation:**

1. Configure the MarkdownHeaderTextSplitter to recognize the MPEP's header structure as represented in the new Markdown file.  
2. The splitter will process the text, creating Document objects. The text content of each object will be the text *under* a specific heading, and the metadata will automatically contain the "breadcrumb" of that section.

Python

\# Python implementation for hierarchical chunking  
from langchain\_text\_splitters import MarkdownHeaderTextSplitter

\# This configuration assumes MPEP section numbers (e.g., 2141\) are   
\# H1 (or '\#') and subsections (e.g., 2141.01) are H2 (or '\#\#').  
\# This must be verified against the generated Markdown file.  
headers\_to\_split\_on \=

markdown\_splitter \= MarkdownHeaderTextSplitter(  
    headers\_to\_split\_on=headers\_to\_split\_on,   
    strip\_headers=False  \# Keep headers in the text for context  
)

\# Load the generated mpep\_2141-2145.md content  
with open("mpep\_2141-2145.md", "r") as f:  
    mpep\_markdown \= f.read()

\# Split the text into structured documents  
docs \= markdown\_splitter.split\_text(mpep\_markdown)

This process results in a list of Document objects where, for example, the text for MPEP § 2141.01 would have metadata like {'Section': '2141...', 'Subsection': '2141.01...'}. This metadata is the key to accurate source citation, fulfilling a core POC objective.

### **1.4 Vectorization and Storage**

The final step of the ingestion pipeline is to embed and store these high-quality Document objects.

1. **Embed:** Using an embedding model (e.g., OpenAI's text-embedding-3-small or a local model), generate a vector embedding for the page\_content of each Document object.  
2. **Store:** Ingest these objects into the proposed vector database (e.g., ChromaDB). The database will store the vector alongside the page\_content and, critically, the metadata containing the MPEP section numbers.

The following table summarizes the chunking strategy analysis.

**Table 1: MPEP Chunking Strategy Comparison**

| Strategy | How It Works | Pros for MPEP | Cons for MPEP |
| :---- | :---- | :---- | :---- |
| **Fixed-Size Chunking** | Slices text by a fixed character or token count. | Simple and fast. | **Unacceptable.** Will split legal rules mid-sentence, destroying context and legal meaning. |
| **Recursive Chunking** | Splits text using a hierarchy of separators (e.g., \\n\\n, \\n, ). | A good general-purpose default for unstructured text. | **High Risk.** Does not understand the MPEP's *numbered* hierarchy. May group unrelated subsections. |
| **Semantic Chunking** | Splits text based on embedding similarity (i.e., by topic). | Conceptually powerful for finding thematic breaks. | **Overkill & Unpredictable.** Adjacent sections in a legal manual are *supposed* to be different topics. |
| **Hierarchical (Markdown Header)** | Splits text based on Markdown header structure (\#, \#\#, etc.). | **Optimal.** Perfectly preserves the logical, legal hierarchy. Creates one chunk per MPEP subsection. Automatically generates metadata for citation. |  |

## **Part 2: Architecting the "Living Text" & "Dynamic Example" Features**

With a high-quality, hierarchically-chunked vector store, the core AI features can be built.

### **2.1 The "Living Text" (Core RAG Pipeline)**

This is the foundational RAG bot and fulfills the first POC objective. It will be built using Python and LangChain. The most important component is the system prompt, which sets the rules, persona, and boundaries for the LLM.

**"Living Text" System Prompt Template:**

Code snippet

SYSTEM: You are "PEP-talk," an expert AI study companion specializing in U.S. Patent Law. Your persona is encouraging, energetic, and precise.

Your knowledge is strictly limited to the provided MPEP sections.

When a user asks a question:  
1\.  Carefully analyze the provided context, which consists of sections from the MPEP.  
2\.  Formulate your answer based \*only\* on this retrieved context.  
3\.  \*\*Crucially, you must cite your sources.\*\* End your answer by citing the exact MPEP section(s) you used, which are available in the context's metadata (e.g., "This is explained in MPEP § 2141.01.").  
4\.  If the provided context does \*not\* contain the answer, you \*must\* follow the "Strict Boundaries" protocol and state that the topic is outside your current knowledge base.

Context:  
{context}

Question:  
{question}

### **2.2 POC Success Criterion: Enforcing "Strict Boundaries"**

A critical POC test is that when asked, "What is the test for anticipation under 102?" the bot *must* respond that this information is outside its knowledge base.

A common "Naive RAG Trap" will cause this test to fail. If the user asks about MPEP 102, the retriever (querying a database that only contains MPEP 103\) will find zero relevant documents. If the RAG chain proceeds to pass the user's question with *no context* to the LLM, the LLM will use its broad pre-trained knowledge to answer the question, thus "hallucinating" and failing the test.

The solution is a "Guardrail" implemented in the application logic *after* retrieval but *before* generation.

**Guardrail Implementation (Python/LangChain Logic):**

Python

\# This logic occurs \*after\* the retriever is called  
\# but \*before\* the LLM generator is called.  
user\_question \= "What is the test for anticipation under 102?"  
retrieved\_docs \= retriever.invoke(user\_question)

\# The relevance\_score\_threshold may need tuning (e.g., 0.2)  
\# For this POC, checking for an empty list is the simplest guardrail.  
if not retrieved\_docs:   
    \# DO NOT CALL THE LLM.  
    \# This hard-coded response guarantees the POC success criterion.  
    response \= "I'm sorry, but that topic is outside my current knowledge base. My expertise is limited to MPEP sections 2141-2145 on Obviousness."  
else:  
    \# Proceed with the RAG chain as normal  
    response \= rag\_chain.invoke({"context": retrieved\_docs, "question": user\_question})

\# return response

This programmatic check is the only way to guarantee 100% compliance with the "Strict Boundaries" requirement.

### **2.3 The "Dynamic Examples" Generator**

This is the second core feature, which generates synthetic, hypothetical examples. This is not a separate bot but a different "mode" of the RAG system. It is a synthetic data generation task that uses the MPEP text as its creative rubric.

The system flow is as follows:

1. The user prompts, "Generate a hypothetical example of a 'motivation to combine' argument."  
2. The system *first* performs a standard RAG query to retrieve the relevant MPEP text (e.g., MPEP § 2143).  
3. This retrieved context is then injected into a *second, specialized prompt template* designed for creative generation. This uses the MPEP context as a "few-shot" or context-grounded example.

**"Dynamic Example" Generation Prompt Template:**

Code snippet

SYSTEM: You are a patent law professor creating a quiz for your students.

Your task is to generate a new, simple, hypothetical scenario that illustrates the legal concept described in the provided MPEP text.

\*\*Instructions:\*\*  
1\.  Read the provided MPEP text.  
2\.  Invent a simple scenario involving:  
    \*   A hypothetical patent claim.  
    \*   A hypothetical Prior Art Reference A.  
    \*   A hypothetical Prior Art Reference B.  
3\.  Write a 1-2 sentence argument that uses the MPEP text's logic to explain the "motivation to combine" A and B to arrive at the claim.  
4\.  Do \*not\* simply repeat the MPEP text. Create a \*new\* example.

\*\*MPEP Context:\*\*  
{context\_from\_rag}

\*\*Generate Scenario:\*\*

This two-step process fulfills the requirement by ensuring the *creative* task is strictly *grounded* in the *factual* MPEP source text.

## **Part 3: Deconstructing and Rebuilding the "PEP-talk" Frontend**

The second primary request is to build a frontend UI inspired by mintlify.com/docs.1 This requires a deconstruction of that site's architecture and a plan to replicate it using the proposed React and TailwindCSS stack.

### **3.1 Architectural Deconstruction of the Mintlify UI**

A review of the Mintlify documentation website 1 reveals its core structure, which is highly suitable for the "PEP-talk" project:

* **Layout:** It uses a classic three-column "Holy Grail" layout.  
  * Column 1 (Left): A resizable, hierarchical sidebar navigation. This is  
    perfect for listing the MPEP sections (2141, 2141.01, etc.).  
  * **Column 2 (Center):** The main content area. This will house both the static MPEP text (for reading) and the interactive chat interface.  
  * **Column 3 (Right):** Contextual content. Mintlify uses this for API code examples. "PEP-talk" can use this panel to display the outputs of the "Dynamic Examples" or "Real-World Connections" features.  
* **Technology:** The mintlify/components open-source repository 2 confirms the site is built with **React** and **TailwindCSS**, perfectly aligning with the project's proposed technology stack.

### **3.2 Step-by-Step Implementation: The React/Tailwind Shell**

1. **Project Setup:** Initialize a new React application and add TailwindCSS.  
   Bash  
   npx create-react-app peptalk-ui \--template-typescript  
   cd peptalk-ui  
   npm install \-D tailwindcss  
   npx tailwindcss init \-p

2. **Configure tailwind.config.js:** Configure the content paths to include all src files.  
3. **Create 3-Column Layout:** Implement the three-column layout in App.js using CSS Flexbox or Grid.  
   JavaScript  
   // App.tsx (Simplified)  
   import React from 'react';

   function App() {  
     return (  
       \<div className\="flex h-screen bg-white text-black"\>  
         {/\* Column 1: Sidebar Navigation \*/}  
         \<nav className\="w-64 shrink-0 bg-gray-50 border-r border-gray-200 p-4 overflow-y-auto"\>  
           {/\* \<SidebarNav /\> will go here \*/}  
           \<h2 className\="font-bold text-lg"\>MPEP 2100\</h2\>  
           {/\* Links... \*/}  
         \</nav\>

         {/\* Column 2: Main Content & Chat \*/}  
         \<main className\="flex-1 p-8 overflow-y-auto"\>  
           {/\* \<ChatInterface /\> will go here \*/}  
           \<h1 className\="text-3xl font-bold mb-4"\>PEP-talk\</h1\>  
         \</main\>

         {/\* Column 3: Contextual Panel \*/}  
         \<aside className\="w-80 shrink-0 bg-gray-100 p-4 overflow-y-auto"\>  
           {/\* \<ContextualPanel /\> will go here \*/}  
           \<h3 className\="font-semibold"\>Contextual Examples\</h3\>  
         \</aside\>  
       \</div\>  
     );  
   }

   export default App;

### **3.3 Building the Core Mintlify-inspired Components**

To capture the "feel" of the Mintlify documentation, several key React components must be built. The Mintlify component library 2 provides clear inspiration.

* **\<SidebarNav\>:** This component will take a JSON representation of the MPEP 2141-2145 hierarchy and recursively render expandable navigation links. This provides the core "study tool" navigation.  
* **\<Callout type="info | warning | danger"\>:** This is an essential component for the AI's responses, allowing it to format "Practitioner Tips" or "Warnings." The Mintlify documentation confirms this component. It is implemented as a React component that accepts a type prop and conditionally applies different TailwindCSS classes (e.g., bg-blue-100 border-blue-500 for "info", bg-red-100 border-red-500 for "danger").  
* **\<CodeBlock\>:** This component is non-negotiable for displaying the output of the "Dynamic Example" and "AI Mock Evaluator" features. Mintlify's docs confirm this component. A library like react-syntax-highlighter can be integrated to provide rich syntax highlighting and a "copy" button.

The following table maps the Mintlify components to their "PEP-talk" function.

**Table 2: Mintlify-inspired Component Map for "PEP-talk"**

| Component Name | Mintlify Purpose | "PEP-talk" Implementation & Purpose |
| :---- | :---- | :---- |
| **SidebarNav** | Hierarchical document navigation. | Renders the MPEP 2141-2145 section hierarchy. Clicking a link could load that section's text into the main panel. |
| **Callout** | Highlight information, warnings, tips. | Used by the AI bot to format responses (e.g., "💡 **PEP-talk Tip:**...") or to display static editor's notes from the MPEP. |
| **CodeBlock** | Display formatted code samples. | **Crucial.** Renders the AI-generated output for "Dynamic Examples" (hypothetical scenarios) and the "AI Evaluator" (mock 103 rejections). |
| **Card** 2 | Clickable, high-level navigation blocks. | Can be used on the app's homepage to "Select a Feature" (e.g., "MPEP Study," "Mock Exam Mode," "Real-World Examples"). |
| **ChatInput** (Custom) | (N/A) | The main user interface for the "Living Text" feature. A standard textarea with a submit button. |

### **3.4 Wiring the Application: Streaming Responses**

To achieve a modern "chatbot" feel, the application must *stream* responses from the backend, not wait for the full response to be generated.

1. **Backend (FastAPI):** The Python backend should use StreamingResponse to stream the LLM's token-by-token output as it is generated.  
2. **Frontend (React):** The React frontend must use the fetch API with a ReadableStream. The application will read chunks from this stream as they arrive and append them to the message state (e.g., setMessages(prev \=\> prev \+ chunk)), creating the "live typing" effect for the user.

## **Part 4: Implementing the Advanced AI Features (The Vertical Slice)**

This section details the implementation of the POC's most innovative features, demonstrating the "thin thread" of the complete, end-to-end architecture.

### **4.1 The "Real-World Connections" POC: A Lightweight File Wrapper Pipeline**

The Phase 2 roadmap, which involves processing the entire USPTO PEDS bulk dataset, represents a massive, multi-month data engineering challenge. For the vertical-slice POC, the goal is not to build this pipeline at scale, but to prove the *architecture* of: **Find \-\> Parse \-\> Tag \-\> Retrieve**.

This architecture can be proven with a "one example" manual pipeline.

**Step-by-Step POC Implementation:**

1. **Find:** The developer will manually use the USPTO Patent Public Search (PPUBS) to find *one* publicly available, abandoned application file wrapper. The target is an application containing a 103 rejection and an applicant response that argues "teaching away".  
2. **Parse:** Download the "Non-Final Rejection" and "Applicant Response" PDF documents from the file wrapper. For the POC, it is essential to select a file with *machine-readable* text. This bypasses the need for complex OCR, which is a separate, large-scale challenge. The pdfplumber library can be used to extract the text.  
3. **Tag:** The *developer* will act as the "AI Classifier" for this one example. They will manually read the applicant's response, identify the 2-3 sentences arguing "teaching away," and copy this text.  
4. **Store:** This tagged data will be stored in a simple real\_world\_examples.json file within the project repository.  
   JSON  
   {  
     "teaching\_away":  
   }

5. **Retrieve:** The application backend will be given a specific rule: if the user asks for a "real-world example of 'teaching away'," it will *not* query the MPEP vector store. Instead, it will load this JSON file, find the "teaching\_away" key, and present that text.

This "vertical slice" successfully demonstrates the complete, end-to-end architecture of the Phase 2 feature without the terabyte-scale data engineering overhead.

### **4.2 The "AI Mock Evaluator" (LLM-as-a-Judge)**

The fourth feature, an AI-powered mock exam evaluator, is a classic "LLM-as-a-judge" pattern. The key to its implementation is the realization that the **MPEP itself is the evaluation rubric**.

The *official* criteria for writing a 103 rejection are detailed in MPEP § 2143 (which lists the required rationales, like "Obvious to Try") and MPEP § 2144 (which explains how to *support* the rejection).

**Step-by-Step Implementation:**

1. The React UI will feature an "Exam Mode."  
2. In this mode, the bot presents a *fixed, static scenario* (e.g., "Here is a claim, Prior Art A, and Prior Art B. Please write a *prima facie* case of obviousness under 35 U.S.C. 103.").  
3. The user submits their answer.  
4. The frontend displays the user's answer (e.g., in a \<CodeBlock\>) and a "Grade Me" button.  
5. Pressing this button triggers a backend call to a specialized "Judge" LLM.  
6. This backend call first performs a RAG query to retrieve the text of MPEP § 2143 and § 2144\. This text is then injected *into the "Judge" prompt* as the official rubric.

The "Judge" prompt template is the core of this feature.

**Table 3: "AI Mock Evaluator" Prompt Template (LLM-as-a-Judge)**

Code snippet

SYSTEM: You are a Supervising Patent Examiner (SPE) at the USPTO. Your task is to critique a Junior Examiner's (the user's) draft rejection based \*only\* on the official MPEP criteria provided below.

You must be constructive, precise, and cite the MPEP criteria in your feedback.

\---  
\*\*YOUR RUBRIC (Official MPEP Criteria):\*\*  
{context\_from\_rag\_for\_MPEP\_2143\_and\_2144}  
\---  
\*\*THE EXAM PROBLEM:\*\*  
\*   \*\*Claim:\*\* "A bicycle with aluminum handlebars and a carbon fiber frame."  
\*   \*\*Prior Art A:\*\* Teaches a bicycle with aluminum handlebars and an aluminum frame.  
\*   \*\*Prior Art B:\*\* Teaches that carbon fiber is a well-known, lightweight, and strong substitute for aluminum in sporting goods.  
\---  
\*\*THE JUNIOR EXAMINER'S (USER'S) DRAFT REJECTION:\*\*  
{user\_answer}  
\---  
\*\*YOUR CRITIQUE:\*\*  
Provide your critique in the following format:

1\.  \*\*What Was Done Correctly:\*\* (e.g., "You correctly identified the prior art references and the difference in the claim.")  
2\.  \*\*What Was Missed:\*\* (e.g., "You failed to articulate a valid \*rationale\* for combining A and B. According to MPEP § 2143(B), this is a 'Simple substitution of one known element for another...' You must state that rationale explicitly.")  
3\.  \*\*Overall Score (out of 10):\*\*  
4\.  \*\*Specific Feedback (citing the MPEP):\*\*

This system provides a high-fidelity evaluation, as the LLM is not just "judging" from its own knowledge but is actively comparing the user's text against the retrieved, authoritative MPEP criteria.

## **Part 5: Strategic Recommendations: Scaling from POC to Full Project**

The vertical-slice POC, when complete, will validate the core architecture. The next steps involve scaling this architecture.

### **5.1 The Phase 2 "Real-World" Data Challenge**

The manual "one example" pipeline in Part 4.1 is a simulation. The full Phase 2 pipeline is the most significant data engineering challenge in the entire project. The PEDS bulk data consists of terabytes of XML and, most problematically, *scanned image PDFs* of varying quality.

A full-scale implementation will require:

* A distributed processing framework (e.g., Apache Spark) to handle the volume.  
* A robust, scalable OCR pipeline to convert millions of scanned, non-machine-readable documents into text.  
* A sophisticated NLP classifier (likely a fine-tuned LLM) to *tag* argument types (e.g., , ) at the sentence level.

This sub-project should be treated as a major data engineering initiative, separate from the core application development.

### **5.2 Designing for the Phase 4 "Domain-Agnostic" Engine**

The POC is, by design, hard-coded for the MPEP. To achieve the Phase 4 goal of a domain-agnostic platform, the ingestion pipeline must be refactored immediately post-POC.

Architectural Recommendation:  
An abstract DataSource interface (or base class) should be created in the Python backend. This class would define standard methods like scrape(), chunk(), and embed().

* The MPEP\_DataSource class will be the first implementation. Its chunk() method will use the MarkdownHeaderTextSplitter logic defined in Part 1.3.  
* A future Medical\_DataSource for textbooks would have a different implementation, perhaps using SemanticChunking to split chapters by topic.  
* A future LegalCode\_DataSource for the CFR would use a different structure-aware splitter.

By isolating the *domain-specific logic* (like the chunking strategy) from the *generic application logic* (the RAG chain, the "Judge" prompt, the UI), the platform can scale to new domains as envisioned.

## **Conclusion**

This blueprint provides a comprehensive, end-to-end implementation plan for the "PEP-talk" vertical-slice proof of concept. It directly addresses the technical requirements for improving the MPEP data scraper by re-framing "styling" as "semantic structure" and providing a hierarchical Markdown-based chunking strategy. It also provides a clear deconstruction of the mintlify.com/docs UI and a component-based plan for its replication in React and TailwindCSS.

By integrating these solutions with the advanced implementation guides for the "Real-World Connections" and "AI Mock Evaluator" features, this plan outlines a clear and achievable path to building the vertical slice. Successful execution of this POC will validate the project's core architectural assumptions and provide a robust foundation for tackling the larger data engineering and platform-generalization challenges of the full project roadmap.

#### **Works cited**

1. Introduction \- Mintlify, accessed November 15, 2025, [https://www.mintlify.com/docs](https://www.mintlify.com/docs)  
2. mintlify/components: UI components for documentation ... \- GitHub, accessed November 15, 2025, [https://github.com/mintlify/components](https://github.com/mintlify/components)