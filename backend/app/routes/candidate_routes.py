"""Candidate routes"""
from flask import Blueprint, request, jsonify, current_app
import os
from werkzeug.utils import secure_filename
from app.services.candidate_service import CandidateService
from app.utils.tfidf_resume_parser import allowed_file

candidate_bp = Blueprint('candidates', __name__, url_prefix='/api/candidates')
candidate_service = CandidateService()

@candidate_bp.route('', methods=['GET'])
def get_candidates():
    """Get all candidates"""
    try:
        candidates = candidate_service.get_all_candidates()
        return jsonify(candidates), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@candidate_bp.route('/<candidate_id>', methods=['GET'])
def get_candidate(candidate_id):
    """Get candidate by ID"""
    try:
        candidate = candidate_service.get_candidate_by_id(candidate_id)
        if candidate:
            return jsonify(candidate), 200
        return jsonify({'error': 'Candidate not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@candidate_bp.route('/upload', methods=['POST'])
def upload_resumes():
    """Upload one or more resumes"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        
        if len(files) == 0:
            return jsonify({'error': 'No files selected'}), 400
        
        upload_folder = current_app.config['UPLOAD_FOLDER']
        uploaded_resumes = []
        
        for file in files:
            if file and allowed_file(file.filename):
                # Save file
                filename = secure_filename(file.filename)
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                
                # Process resume
                try:
                    candidate_data = candidate_service.upload_resume(file_path)
                    uploaded_resumes.append(candidate_data)
                    
                    # Clean up uploaded file
                    if os.path.exists(file_path):
                        os.remove(file_path)
                
                except Exception as e:
                    print(f"[ERROR] Error in upload route: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    return jsonify({
                        'error': f'Error processing {filename}: {str(e)}'
                    }), 500
            else:
                return jsonify({
                    'error': f'File {file.filename} not allowed. Only PDF and DOCX files are accepted.'
                }), 400
        
        try:
            response_data = {
                'message': f'Successfully uploaded {len(uploaded_resumes)} resume(s)',
                'candidates': uploaded_resumes
            }
            print(f"[UPLOAD] Response data prepared: {len(response_data['candidates'])} candidates")
            return jsonify(response_data), 201
        except Exception as e:
            print(f"[ERROR] Error building response: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Error building response: {str(e)}'}), 500
    
    except Exception as e:
        print(f"[ERROR] Unexpected error in upload: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@candidate_bp.route('/search', methods=['POST'])
def search_candidates():
    """Search candidates"""
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query']
        filters = data.get('filters', {})
        
        results = candidate_service.search_candidates(query, filters)
        
        return jsonify({
            'candidates': results,
            'total': len(results),
            'query': query
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@candidate_bp.route('', methods=['DELETE'])
def delete_candidates():
    """Delete all candidates"""
    try:
        result = candidate_service.delete_all_candidates()
        return jsonify({
            'message': 'All candidates deleted',
            **result
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@candidate_bp.route('/<candidate_id>/status', methods=['PUT'])
def update_candidate_status(candidate_id):
    """Update candidate status"""
    try:
        data = request.get_json()
        
        if not data or 'status' not in data:
            return jsonify({'error': 'Status is required'}), 400
        
        status = data['status']
        
        if status not in ['Active', 'Selected', 'Rejected']:
            return jsonify({'error': 'Invalid status'}), 400
        
        result = candidate_service.update_candidate_status(candidate_id, status)
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
