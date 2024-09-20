from django.shortcuts import render
from django.http import JsonResponse
from .tasks import fetch_twitter_data
from celery.result import AsyncResult


def home(request):
    print(f"Triggering task with username: clevermike_a")  # Log username
    task = fetch_twitter_data.delay("clevermike_a")
    print(task.id)
    return render(request, "index.html")


def trigger_twitter_task_view(request, username):
    if request.method == "POST":
        print(f"Triggering task with username: {username}")  # Log username
        task = fetch_twitter_data.delay("clevermike_a")

        return JsonResponse(
            {"task_id": task.id, "status": "Task has been started successfully."}
        )

    return JsonResponse({"error": "Invalid request method"}, status=400)


# View to check task status by task ID
def check_task_status_view(request, task_id):
    task_result = AsyncResult(task_id)

    # Get the current task status (e.g., PENDING, SUCCESS, FAILURE)
    status = task_result.status
    result = None

    # If the task is successful, get the result
    if task_result.successful():
        result = task_result.result

    return JsonResponse({"task_id": task_id, "status": status, "result": result})
