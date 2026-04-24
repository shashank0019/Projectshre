"""Candidate routes"""
from fastapi import APIRouter, Request, UploadFile, File, HTTPException
import os
from app.services.candidate_service import CandidateService
from app.utils.tfidf_resume_parser import allowed_file

candidate_bp = APIRouter(prefix='/candidates', tags=['candidates'])
candidate_service = CandidateService()

@candidate_bp.post('/search')
async def search_candidates(request: Request):
    """Search candidates"""
    try:
        data = await request.json()
        
        if not data or 'query' not in data:
            raise HTTPException(status_code=400, detail='Query is required')
        
        query = data['query']
        filters = data.get('filters', {})
        
        results = candidate_service.search_candidates(query, filters)
        
        return {
            'candidates': results,
            'total': len(results),
            'query': query
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@candidate_bp.post('/upload')
async def upload_resumes(request: Request, files: list[UploadFile] = File(...)):
    """Upload one or more resumes"""
    try:
        if not files:
            raise HTTPException(status_code=400, detail='No files selected')
        
        upload_folder = request.app.config.UPLOAD_FOLDER
        uploaded_resumes = []
        
        for file in files:
            if file and allowed_file(file.filename):
                try:
                    # Save file
                    filename = file.filename
                    file_path = os.path.join(upload_folder, filename)
                    
                    content = await file.read()
                    with open(file_path, 'wb') as f:
                        f.write(content)
                    
                    # Process resume
                    candidate_data = candidate_service.upload_resume(file_path)
                    uploaded_resumes.append(candidate_data)
                    
                    # Clean up uploaded file
                    if os.path.exists(file_path):
                        os.remove(file_path)
                
                except Exception as e:
                    print(f"[ERROR] Error in upload route: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    raise HTTPException(status_code=500, detail=f'Error processing {file.filename}: {str(e)}')
            else:
                raise HTTPException(status_code=400, detail=f'File {file.filename} not allowed. Only PDF and DOCX files are accepted.')
        
        response_data = {
            'message': f'Successfully uploaded {len(uploaded_resumes)} resume(s)',
            'candidates': uploaded_resumes
        }
        print(f"[UPLOAD] Response data prepared: {len(response_data['candidates'])} candidates")
        return response_data
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Unexpected error in upload: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@candidate_bp.get('')
async def get_candidates():
    """Get all candidates"""
    try:
        candidates = candidate_service.get_all_candidates()
        return candidates
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@candidate_bp.get('/{candidate_id}')
async def get_candidate(candidate_id: str):
    """Get candidate by ID"""
    try:
        candidate = candidate_service.get_candidate_by_id(candidate_id)
        if candidate:
            return candidate
        raise HTTPException(status_code=404, detail='Candidate not found')
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@candidate_bp.delete('')
async def delete_candidates():
    """Delete all candidates"""
    try:
        result = candidate_service.delete_all_candidates()
        return {
            'message': 'All candidates deleted',
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@candidate_bp.put('/{candidate_id}/status')
async def update_candidate_status(candidate_id: str, request: Request):
    """Update candidate status"""
    try:
        data = await request.json()
        
        if not data or 'status' not in data:
            raise HTTPException(status_code=400, detail='Status is required')
        
        status = data['status']
        
        if status not in ['Active', 'Selected', 'Rejected']:
            raise HTTPException(status_code=400, detail='Invalid status')
        
        result = candidate_service.update_candidate_status(candidate_id, status)
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
