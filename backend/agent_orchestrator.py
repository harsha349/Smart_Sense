# import os, json, time, base64
# from google.cloud import storage, firestore
# try:
#     from vertexai import client as vertex_client
#     from vertexai import language as vertex_language
#     from vertexai import Vision
# except Exception:
#     vertex_client = None
#     vertex_language = None
#     Vision = None

# # Load nutrition DB
# NUTRITION_DB_PATH = os.environ.get('NUTRITION_DB_PATH','backend/nutrition_db.json')
# try:
#     with open(NUTRITION_DB_PATH,'r') as f:
#         NUT_DB = json.load(f)
# except Exception:
#     NUT_DB = {}

# PROJECT = os.environ.get('GOOGLE_CLOUD_PROJECT')
# REGION = os.environ.get('REGION','asia-south1')
# BUCKET = os.environ.get('BUCKET_NAME')

# db = firestore.Client() if PROJECT else None
# storage_client = storage.Client() if PROJECT else None

# TEXT_MODEL = 'gemini-1.5-flash'

# def call_text_model(prompt, max_tokens=800):
#     if vertex_language:
#         model = vertex_language.TextGenerationModel.from_pretrained(TEXT_MODEL)
#         resp = model.predict(prompt, max_output_tokens=max_tokens)
#         return resp.text
#     else:
#         return 'FALLBACK: ' + prompt[:400]

# def base64_encode(bts):
#     return base64.b64encode(bts).decode('utf-8')

# def vision_detect_items(image_bytes):
#     # Try Vertex Vision
#     if Vision:
#         try:
#             vc = Vision.VisionClient()
#             resp = vc.predict_image(content=image_bytes)
#             labels = []
#             for lab in getattr(resp, 'labels', []):
#                 labels.append({'name': lab.display_name.lower(), 'confidence': float(getattr(lab,'confidence',0.9)), 'approx_qty':'', 'freshness':'unknown'})
#             return {'items': labels, 'raw_text': ', '.join([l['name'] for l in labels])}
#         except Exception as e:
#             print('Vision SDK failed:', e)
#     # Fallback: ask text model with base64
#     b64 = base64_encode(image_bytes)
#     prompt = f"You are an image interpreter. Given this base64 image, list visible food items as JSON: {{\"items\":[], \"raw_text\":\"\"}}. Image(base64): {b64}"
#     txt = call_text_model(prompt, max_tokens=400)
#     try:
#         start = txt.find('{')
#         obj = json.loads(txt[start:])
#         return obj
#     except Exception:
#         items = [{'name': w.strip().lower(), 'confidence':0.8, 'approx_qty':'', 'freshness':'unknown'} for w in txt.split(',')[:10]]
#         return {'items': items, 'raw_text': txt}

# def planner_agent(vision_out, user_diet):
#     prompt = f"Planner: items: {vision_out.get('raw_text','')}. user_diet:{user_diet}. Return JSON with keys user_diet,prioritize,steps,notes."
#     txt = call_text_model(prompt, max_tokens=200)
#     try:
#         start = txt.find('{'); plan = json.loads(txt[start:])
#     except:
#         plan = {'user_diet':user_diet,'prioritize':['use_soon','quick'],'steps':['nutrition','recipes','grocery'],'notes':''}
#     return plan

# def nutrition_agent(vision_out, servings=2):
#     ingredients = []
#     totals = {'cal':0,'protein':0,'carbs':0,'fat':0,'fiber':0}
#     for it in vision_out.get('items',[]):
#         name = it.get('name','').lower()
#         entry = NUT_DB.get(name)
#         qty_g = 100
#         if it.get('approx_qty'):
#             try:
#                 qty_g = int(it['approx_qty'])
#             except:
#                 qty_g = 100
#         if entry:
#             factor = qty_g / 100.0
#             totals['cal'] += entry.get('cal',0)*factor
#             totals['protein'] += entry.get('protein',0)*factor
#             totals['carbs'] += entry.get('carbs',0)*factor
#             totals['fat'] += entry.get('fat',0)*factor
#             totals['fiber'] += entry.get('fiber',0)*factor
#         ingredients.append({'name':name,'qty_g':qty_g,'per_100g':entry})
#     for k in totals:
#         totals[k] = round(totals[k]/max(1,servings),2)
#     return {'ingredients':ingredients,'totals_per_serving':totals}

# def recipe_agent(ingredient_list, user_diet, prioritize):
#     prompt = f"You are chef+dietician. Ingredients: {ingredient_list}. user_diet:{user_diet}. prioritize:{prioritize}. Return valid JSON with 3 recipe objects including nutrition fields."
#     txt = call_text_model(prompt, max_tokens=1000)
#     try:
#         start = txt.find('{'); recipes = json.loads(txt[start:])
#     except:
#         recipes = {'recipes':[{'title':'Simple Omelette','servings':2,'time':'10m','difficulty':'easy','ingredients':[{'name':'egg','qty':'2'}],'steps':['beat eggs','cook'],'nutrition_per_serving':{'cal':200}}]}
#     return recipes

# def health_agent(recipe_obj):
#     prompt = f"For recipe: {recipe_obj}. Return JSON health_summary,warnings,score"
#     txt = call_text_model(prompt, max_tokens=300)
#     try:
#         start = txt.find('{'); res = json.loads(txt[start:])
#     except:
#         res = {'health_summary':'Balanced protein-rich meal','warnings':[],'score':8}
#     return res

# def grocery_agent(recipes):
#     prompt = f"Given these recipes {recipes}, list missing ingredients consolidated and suggest substitutes as JSON."
#     txt = call_text_model(prompt, max_tokens=300)
#     try:
#         start = txt.find('{'); res = json.loads(txt[start:])
#     except:
#         res = {'shopping_list':[],'substitutes':[]}
#     return res

# def persist_result(user_id, payload):
#     if not db:
#         return None
#     doc = db.collection('scans').document()
#     doc.set({'user_id':user_id,'payload':payload,'ts':int(time.time())})
#     return doc.id

# def orchestrate(image_bytes, user_diet='none', user_id='anonymous'):
#     vision_out = vision_detect_items(image_bytes)
#     plan = planner_agent(vision_out, user_diet)
#     nutrition_out = nutrition_agent(vision_out, servings=2)
#     ingredient_list = [it['name'] for it in vision_out.get('items',[])]
#     recipes_out = recipe_agent(ingredient_list, plan.get('user_diet','none'), plan.get('prioritize',[]))
#     health_results = []
#     for rec in recipes_out.get('recipes', []):
#         health_results.append(health_agent(rec))
#     grocery_out = grocery_agent(recipes_out)
#     final = {'vision':vision_out,'plan':plan,'nutrition':nutrition_out,'recipes':recipes_out,'health':health_results,'grocery':grocery_out}
#     docid = persist_result(user_id, final)
#     final['id'] = docid
#     return final
#...................................abs



import random

def orchestrate(img_bytes, user_diet="none", user_id="anonymous"):
    """
    Mock orchestrator for testing the UI. Returns realistic
    food detection, nutrition, health summary, recipes, and grocery plan.
    """
    
    # Mock detected items
    items = [
        {"name": "tomato", "confidence": 0.95, "freshness": "fresh", "approx_qty": "2 pcs"},
        {"name": "egg", "confidence": 0.9, "freshness": "fresh", "approx_qty": "2 pcs"},
        {"name": "spinach", "confidence": 0.85, "freshness": "fresh", "approx_qty": "100g"}
    ]
    
    # Nutrition totals
    nutrition_totals = {"cal": 250, "protein": 15, "carbs": 10, "fat": 12, "fiber": 5}
    
    # Health summary
    health = [{"health_summary": "Balanced protein-rich meal", "score": 8, "warnings": []}]
    
    # Recipes
    recipes = {
        "recipes": [
            {
                "title": "Simple Omelette",
                "difficulty": "easy",
                "ingredients": [{"name": "egg", "qty": "2"}, {"name": "spinach", "qty": "50g"}],
                "steps": ["beat eggs", "add spinach", "cook in pan"],
                "time": "10m",
                "servings": 1,
                "nutrition_per_serving": {"cal": 200, "protein": 12, "carbs": 3, "fat": 10}
            }
        ]
    }
    
    # Grocery plan
    grocery = {"shopping_list": ["tomato", "egg", "spinach"], "substitutes": ["kale instead of spinach"]}
    
    # Plan
    plan = {
        "notes": "Use fresh ingredients for best taste",
        "prioritize": ["use_soon", "quick"],
        "steps": ["nutrition", "recipes", "grocery"],
        "user_diet": user_diet
    }
    
    return {
        "vision": {"items": items, "raw_text": "Detected items from image"},
        "nutrition": {"ingredients": items, "totals_per_serving": nutrition_totals},
        "health": health,
        "recipes": recipes,
        "grocery": grocery,
        "plan": plan,
        "id": user_id
    }