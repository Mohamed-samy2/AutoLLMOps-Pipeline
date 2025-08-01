from fastapi.responses import JSONResponse
from fastapi import APIRouter , status,Depends,Header,HTTPException,Request
from config.config import get_settings
from controllers.data_controller.data_controller import data_controller
from controllers.training_controller.training_controller import training_controller
from controllers.research_controller.research_controller import research_controller

llm_finetuning = APIRouter(tags=['FineTuning'], prefix='/api/v1')
    

@llm_finetuning.get("/start_finetuning")
async def finetune(request: Request, settings: tuple = Depends(get_settings)):
    """Endpoint to process user messages and return chatbot responses."""

    # researcher = research_controller(llm = request.app.llm,checkpointer=request.app.checkpointer, db_client=request.app.db_client) 
    # print(f"Starting Research for domain: {settings.TARGET_DOMAIN}")
    # is_research_finished = await researcher.run(settings.TARGET_DOMAIN)
    
    # if not is_research_finished:
    #     print("Research failed to complete.")
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Research failed to complete.")
    # print("Research completed successfully. Starting data processing...")
    # data = data_controller(settings=settings, llm=request.app.llm, db_client=request.app.db_client)

    # is_data_finished= await data.run()
    
    # if not is_data_finished:
    #     print("Data processing failed to complete.")
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Data processing failed to complete.")
    
    print("Data processing completed successfully. Starting training...")
    trainer = training_controller(base_llm=settings.BASE_LLM, db_client=request.app.db_client)
    
    is_training_finished = await trainer.run()
    
    if not is_training_finished:
        print("Training failed to complete.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Training failed to complete.")
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Fine-tuning process completed successfully.",
            "status": "success"
        }
    )