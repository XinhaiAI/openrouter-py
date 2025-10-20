import requests

# --- 配置 (Configuration) ---
API_URL = "https://openrouter.ai/api/v1/models"

# 在这里配置你想要检查的模型，用分号 ; 隔开
# Configure the models you want to check here, separated by semicolons ;
MODELS_TO_CHECK = "gpt-oss-20b;deepseek-r1;qwen"


# --- 函数定义 (Function Definitions) ---

def fetch_models():
    """
    从 OpenRouter API 获取模型列表。
    Fetches the list of models from the OpenRouter API.
    """
    try:
        response = requests.get(API_URL, timeout=15)
        response.raise_for_status() # 如果请求失败 (例如 404, 500)，则会抛出异常 (Raises an exception for bad responses like 404 or 500)
        
        # 确保API返回了'data'键 (Ensure the API response contains the 'data' key)
        data = response.json()
        if "data" not in data:
            print("错误 (Error): API响应中未找到'data'字段 (The 'data' field was not found in the API response).")
            return None
        return data["data"]
    except requests.exceptions.RequestException as e:
        print(f"错误 (Error): 无法连接到 OpenRouter API (Unable to connect to the OpenRouter API).")
        print(f"详情 (Details): {e}")
        return None
    except requests.exceptions.JSONDecodeError:
        print("错误 (Error): 无法解析API的响应，可能不是有效的JSON格式 (Failed to parse the API response, it might not be valid JSON).")
        return None


def check_specific_models(models_to_check_str, all_models):
    """
    检查指定的模型名称，优先显示免费版本及其上下文长度。
    Checks the specified model names, prioritizing the display of free versions and their context lengths.
    """
    print(f"\n{'=' * 15} 指定模型可用性检查 (Specific Model Availability Check) {'=' * 15}")
    
    if not all_models:
        print("无法执行检查，因为未能获取到模型列表。 (Cannot perform check because the model list could not be fetched.)")
        return

    model_names_to_check = [name.strip() for name in models_to_check_str.split(';')]

    for name in model_names_to_check:
        print(f"\n查询 (Query): '{name}'")
        found_free_models = []
        found_non_free_models = []

        # 遍历所有模型，收集匹配项 (Iterate through all models to collect matches)
        for model in all_models:
            model_id = model.get('id', '')
            if name in model_id:
                if model_id.endswith(':free'):
                    found_free_models.append(model)
                else:
                    found_non_free_models.append(model)
        
        # 优先输出免费模型 (Prioritize displaying free models)
        if found_free_models:
            print(f"-> 状态 (Status): 是免费的 (Free)")
            print(f"   {'模型 ID (Model ID)':<60} {'上下文长度 (Context Length)':>25}")
            print(f"   {'-'*60} {'-'*25}")
            for model in found_free_models:
                context_len = f"{model.get('context_length', 0):,}"
                print(f"   - {model.get('id'):<58} {context_len:>25}")
        
        # 如果没有免费模型，再输出非免费模型 (If no free models are found, then display non-free models)
        elif found_non_free_models:
            print(f"-> 状态 (Status): 非免费 (Not Free)")
            print(f"   {'模型 ID (Model ID)':<60} {'上下文长度 (Context Length)':>25}")
            print(f"   {'-'*60} {'-'*25}")
            for model in found_non_free_models:
                context_len = f"{model.get('context_length', 0):,}"
                print(f"   - {model.get('id'):<58} {context_len:>25}")

        # 如果什么都没找到 (If nothing is found)
        else:
            print("-> 状态 (Status): 未找到任何相关模型 (No related models found)")


def filter_free_models(models):
    """
    从模型列表中筛选出所有免费模型。
    Filters out all free models from the model list.
    """
    if not models:
        return []
    
    free_models = []
    for model in models:
        if model.get('id', '').endswith(':free'):
            free_models.append(model)
    return free_models


def display_free_models_with_supplier(models):
    """
    创建一个文本表格来展示所有免费模型的信息，并按供应商排序。
    Creates a text table to display information for all free models, sorted by supplier.
    """
    title = "OpenRouter 全部免费模型列表 (按供应商排序) (All Free Models on OpenRouter (Sorted by Supplier))"
    print(f"\n{'=' * 15} {title} {'=' * 15}")

    if not models:
        print("没有找到任何免费模型。 (No free models found.)")
        return

    # 关键改动：按供应商和模型ID进行排序
    # Key change: Sort by supplier (creator) and then by model ID.
    # 'z' is a default value to ensure items without an ID are sorted last.
    sorted_models = sorted(models, key=lambda m: (m.get('id', 'z').split('/')[0], m.get('id', '')))

    print(f"{'供应商 (Supplier)':<30} {'模型 ID (Model ID)':<60} {'上下文长度 (Context Length)':>25}")
    print(f"{'-' * 30} {'-' * 60} {'-' * 25}")

    for model in sorted_models:
        model_id = model.get('id', 'N/A')
        supplier = model_id.split('/')[0] if '/' in model_id else 'N/A'
        context_length = f"{model.get('context_length', 0):,}"
        print(f"{supplier:<30} {model_id:<60} {context_length:>25}")


# --- 程序入口 (Program Entry Point) ---
if __name__ == "__main__":
    print("正在从 OpenRouter 获取模型数据... (Fetching model data from OpenRouter...)")
    all_models_data = fetch_models()

    if all_models_data:
        print("数据获取成功！ (Data fetched successfully!)")
        
        # 第一步：检查你指定的模型
        # Step 1: Check the models you specified.
        check_specific_models(MODELS_TO_CHECK, all_models_data)
        
        # 第二步：筛选并列出所有免费模型，并按供应商排序
        # Step 2: Filter and list all free models, sorted by supplier.
        free_models_list = filter_free_models(all_models_data)
        display_free_models_with_supplier(free_models_list)
