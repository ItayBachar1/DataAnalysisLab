![header](https://capsule-render.vercel.app/api?type=waving&color=A5BECC&height=300&section=header&text=Data%20Analysis%20Lab-nl-&fontSize=65&animation=fadeIn&fontColor=243A73&desc=Final%20Project&descSize=52&stroke=243A73&strokeWidth=0)
![header](https://capsule-render.vercel.app/api?type=transparent&color=A5BECC&height=65&reversal=true&fontSize=24&fontColor=365486&text=The%20Faculty%20of%20Data%20and%20Decisions%20Science%20-nl-%20&desc=%20Technion%20-%20Israel%20Institute%20of%20Technology&descSize=18&descAlignY=73&fontAlign=50&animation=fadeIn&textBg=false&section=header&stroke=243A73&strokeWidth=0&theme=holi)
![footer](https://capsule-render.vercel.app/api?type=waving&color=A5BECC&height=100&section=footer&text=%20-nl-%20Spring%202023/24%20%20&fontSize=16&fontAlign=50&fontColor=243A73&theme=holi)

![header](https://capsule-render.vercel.app/api?type=soft&color=293B5F&height=45&section=header2&text=Authors&fontSize=28&fontAlign=7&fontColor=EEF5FF&reversal=false&theme=holi)
> Itay Bachar itaybachar@campus.technion.ac.il
> 
> Sewar Hino sewar.hino@campus.technion.ac.il
> 
> Adir Toledano adir1905@campus.technion.ac.il
> 
![header](https://capsule-render.vercel.app/api?type=soft&color=293B5F&height=45&section=header&text=Overview&fontSize=33&fontAlign=10&fontColor=EEF5FF&reversal=true&theme=holi)

This project demonstrates a Retrieval-Augmented Generation (RAG) system designed to provide personalized property recommendations for Airbnb listings. By combining vector database technologies (FAISS and Pinecone) with language models (distilgpt2 and all-MiniLM-L6-v2), the system retrieves relevant listings based on user preferences and generates coherent responses tailored to specific queries.

The project includes:
- A RAG system with two indexing methods (FAISS and Pinecone).
- A synthetic QA dataset generated using Cohere’s LLM for evaluation.
- A demo application with an interactive user interface for real-time recommendations.


![header](https://capsule-render.vercel.app/api?type=soft&color=293B5F&height=45&section=header&text=Setup%20Instructions&fontSize=28&fontAlign=15&fontColor=EEF5FF&reversal=true&theme=holi)

#### 1. Clone the repository:
```bash
git clone https://github.com/ItayBachar1/DataAnalysisLab.git
```
#### 2. Navigate to the project directory:
```bash
cd DataAnalysisLab
```
#### 3. Install the necessary dependencies:
```bash
pip install -r requirements.txt
```
![header](https://capsule-render.vercel.app/api?type=soft&color=293B5F&height=45&section=header&text=Run%20Instructions&fontSize=28&fontAlign=14&fontColor=EEF5FF&reversal=true&theme=holi)

Run the FastAPI backend server:
```bash
uvicorn fastapi_app:app --reload    
```
Run the Streamlit frontend app:
```bash
streamlit run streamlit_app.py
```
