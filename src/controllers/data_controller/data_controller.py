import logging
import os
from langchain_core.messages import HumanMessage,SystemMessage
from.schemas.QASchema import QAList
import fitz
import json
from .prompts.qa_prompts import qa_prompts
import time
class data_controller:
    def __init__(self, settings, llm, db_client):
        self.llm = llm
        self.db_client = db_client
        self.settings=settings
        self.logger = logging.getLogger('uvicorn')
    
    async def run(self):
        
        self.logger.info("Starting data processing...")
        
        await self.process_documents()
        await self.process_db()
        
        self.logger.info("Data processing completed successfully.")
        
        return True
    
    async def call_model(self,message):
        time.sleep(10)  # Adding a delay to avoid rate limiting issues
        system_prompt = SystemMessage(content=qa_prompts.QA_SYSTEM_PROMPT.value)
    
        chat_messages = [system_prompt] + [HumanMessage(content=message)]
        response = await self.llm.generate_response(messages=chat_messages,response_schema=QAList)
        
        return response
    
    async def process_documents(self):
        
        if not os.path.exists(self.settings.DATA_SOURCES_PATH) or len(os.listdir(self.settings.DATA_SOURCES_PATH)) == 0:
            self.logger.error(f"Data sources path does not exist: {self.settings.DATA_SOURCES_PATH}")
            return
        
        for file_name in os.listdir(self.settings.DATA_SOURCES_PATH):
            
            if file_name.endswith('.pdf'):
                file_path = os.path.join(self.settings.DATA_SOURCES_PATH, file_name)
                pdf_document = fitz.open(file_path)
                i=0
                for page_num in range(pdf_document.page_count):
                    
                    page = pdf_document[page_num]
                    
                    page_text = page.get_text()
                    q_a_pairs = await self.call_model(page_text)
                    
                    if q_a_pairs:
                        if i % 3 == 0:
                            await self.db_client.insert_qa(q_a_pairs.items, type='val')
                        else:
                            await self.db_client.insert_qa(q_a_pairs.items, type='train')
                        i += 1
                        self.logger.info(f"Processed page {page_num + 1} of {file_name} and inserted Q&A pairs into the database.")
                    else:
                        self.logger.warning(f"No Q&A pairs generated for page {page_num + 1} of {file_name}.")
                    
            elif file_name.endswith('.txt'):
                file_path = os.path.join(self.settings.DATA_SOURCES_PATH, file_name)
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()

                q_a_pairs = await self.call_model(file_content)

                if q_a_pairs:
                    await self.db_client.insert_qa(q_a_pairs.items, type='train')
                    self.logger.info(f"Processed {file_name} and inserted Q&A pairs into the database.")
                else:
                    self.logger.warning(f"No Q&A pairs generated for {file_name}.")
        
        return True
    
    async def process_db(self):
        i = 0
        async for row in self.db_client.get_raw_text():

            text = row[1]
            metadata = row[2]
            full_text = text + "\n" + f"Metadata: {json.dumps(metadata, ensure_ascii=False)}\n\n"
            q_a_pairs = await self.call_model(full_text)
    
            if q_a_pairs:
                if i % 3 == 0:
                    await self.db_client.insert_qa(q_a_pairs.items, type='val')
                else:
                    await self.db_client.insert_qa(q_a_pairs.items, type='train')
                i += 1
                self.logger.info(f"Processed row {row[0]} and inserted Q&A pairs into the database.")
            else:
                self.logger.warning(f"No Q&A pairs generated for row {row[0]}.")
                
        return True

