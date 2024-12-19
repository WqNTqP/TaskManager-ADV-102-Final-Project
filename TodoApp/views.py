from django.shortcuts import render, redirect
from .models import TaskMate_userDetails, TaskMate_taskDetails
from django.utils import timezone
from datetime import datetime

def myDayView(request):
    data = {}
    if request.session.has_key('username'):
        username = request.session['username']
        
        # Get today's date in the format you are using in your tasks
        today_date = datetime.now().date().strftime('%Y-%m-%d')  # Adjust format as needed

        # Retrieve tasks that are due today
        tasks_today = TaskMate_taskDetails.objects.filter(userName=username, deadlineDate=today_date).order_by('deadlineTime').values()

        data['tasks'] = tasks_today
        return render(request, 'myday.html', data)
    else:
        return redirect('login')

def login(request):
    if request.session.has_key('username'):
        return redirect('homepage')
    else:
        data = {'error': None }
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']

            # Authenticate user
            user = TaskMate_userDetails.objects.filter(username=username, password=password).first()
            if user:
                request.session['username'] = username
                
                # Check if the user is an admin
                if user.role == 'admin':
                    return redirect('homepage')  # Redirect to admin homepage
                else:
                    return redirect('userDashboard')  # Redirect to user dashboard for regular users
            else:
                data['error'] = "Invalid Credentials"
                return render(request, 'login.html', data)

        return render(request, 'login.html')

def homepage(request):
    # Initialize data dictionary
    data = {}
    
    # Check if the user is logged in
    if request.session.has_key('username'):
        username = request.session['username']

        # Retrieve the user object to check the role
        user = TaskMate_userDetails.objects.get(username=username)

        # Check if the user is an admin
        if user.role != 'admin':
            return redirect('userDashboard')  # Redirect regular users to their dashboard

        # Handle task creation
        if request.method == "POST":
            q_data = request.POST
            date = q_data.get('date')
            time = q_data.get('time')
            priority = q_data.get('priority')
            description = q_data.get('description')

            try:
                # Create and save the new task
                task = TaskMate_taskDetails(
                    userName=username,
                    deadlineDate=date,
                    deadlineTime=time,
                    priority=priority,
                    description=description
                )
                task.save()
                # Redirect to the homepage after saving the task to prevent resubmission
                return redirect('homepage')
            except Exception as e:
                print(f"Error saving task: {e}")
                data['error'] = "There was an error saving your task. Please try again."

        # Retrieve all tasks for the admin, including accepted tasks
        try:
            tasks = TaskMate_taskDetails.objects.all().order_by('deadlineDate', 'deadlineTime', 'priority')
            data['tasks'] = tasks  # Prepare data to send to the template
        except Exception as e:
            print(f"Error retrieving tasks: {e}")
            data['error'] = "There was an error retrieving tasks. Please try again."

        # Check for acceptance message
        accept_message = request.session.pop('accept_message', None)  # Get and remove the message from the session
        data['accept_message'] = accept_message  # Pass the message to the template

        # Render the homepage with the tasks
        return render(request, 'homepage.html', data)
    else:
        return redirect('login')  # Redirect to login if the user is not logged in

def signUp(request):
    data = {}
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirmpassword = request.POST.get("confirmpassword")
        role = request.POST.get("role")  # Get the selected role

        if password != confirmpassword:
            data["error"] = "Passwords do not match"
            return render(request, 'signup.html', data)
        else:
            if TaskMate_userDetails.objects.filter(username=username).exists():
                data["error"] = "Username already exists"
                return render(request, 'signup.html', data)
            elif TaskMate_userDetails.objects.filter(email=email).exists():
                data["error"] = "Email already exists"
                return render(request, 'signup.html', data)
            else:
                try:
                    # Create the user with role
                    user = TaskMate_userDetails(username=username, email=email, password=password, role=role)
                    user.save()
                    data["error"] = "Account created successfully"
                    return render(request, 'signup.html', data)
                except Exception as e:
                    data["error"] = "Something went wrong"
                    return render(request, 'signup.html', data)
    else:
        data["error"] = None
        return render(request, 'signup.html', data)

def resetPassword(request):
    data = {}
    return render(request, 'resetPassword.html', data)

def profilePage(request):
    if request.session.has_key('username'):
        if request.method == 'POST':
            profilePic = request.POST.get('photo')
            if profilePic == '':
                x = TaskMate_userDetails.objects.filter(username=request.session['username']).values()
                profilePic = x[0]['profilePic']

            fullName = request.POST.get('fullname')
            mobile = request.POST.get('mobile')
            bio = request.POST.get('bio')

            try:
                TaskMate_userDetails.objects.filter(username=request.session['username']).update(profilePic=profilePic, fullName=fullName, mobileNumber=mobile, bio =bio)
            except Exception as e:
                print(e)

        x = TaskMate_userDetails.objects.filter(username=request.session['username']).values()
        data = {'details': x[0]}
        return render(request, 'profilePage.html', data)
    else:
        return redirect('login')

def logOut(request):
    del request.session['username']
    return redirect('login')

def delete(request, idd):
    if request.session.has_key('username'):
        admin_username = request.session['username']  # Get the admin's username
        task = TaskMate_taskDetails.objects.filter(taskId=idd).first()  # Get the task to be deleted

        if task:
            # Retrieve the user object to check the role
            user = TaskMate_userDetails.objects.get(username=admin_username)

            # Check if the user is an admin
            if user.role == 'admin':
                # Store the message in the session to display on the user dashboard
                message = f"The Task was Canceled By {admin_username}"
                request.session['delete_message'] = message
                
                # Store task details for display
                task_details = {
                    'description': task.description,
                    'deadlineDate': task.deadlineDate,
                    'deadlineTime': task.deadlineTime,
                    'priority': task.priority,
                }
                request.session['deleted_task'] = task_details
                
                # Delete the task
                task.delete()
            else:
                # If the user is not an admin, check if the task is accepted
                if task.status == 'In Progress':  # Assuming 'In Progress' indicates the task has been accepted
                    # Optionally, you can set an error message indicating that accepted tasks cannot be deleted
                    request.session['error_message'] = "Cannot delete an accepted task."
                    return redirect('homepage')  # Redirect back to the homepage or wherever appropriate

                # If the task is not accepted, allow deletion
                task.delete()

        return redirect('homepage')  # Redirect back to the homepage after deletion
    else:
        return redirect('login')
    
def editTodo(request, idd):
    data = {'idd': idd}
    user = request.session['username']
    
    if request.method == 'POST':
        q_data = request.POST
        date = q_data.get('date')
        time = q_data.get('time')
        priority = q_data.get('priority')
        description = q_data.get('description')

        try:
            # Update the task details
            TaskMate_taskDetails.objects.filter(taskId=idd, userName=user).update(
                deadlineDate=date,
                deadlineTime=time,
                priority=priority,
                description=description
            )
            return redirect('homepage')
        except Exception as e:
            print(f"Error updating task: {e}")

    # Retrieve the task details
    x = TaskMate_taskDetails.objects.filter(taskId=idd, userName=user).values()
    
    if not x:  # Check if the task exists
        # Optionally, you can add a message to inform the user
        return redirect('homepage')  # Redirect if the task does not exist

    data['todo'] = x[0]  # Safely access the first item since we checked if it exists
    return render(request, "edittodo.html", data)

def userDashboard(request):
    data = {}
    if request.session.has_key('username'):
        username = request.session['username']
        
        # Retrieve user-specific tasks
        user_tasks = TaskMate_taskDetails.objects.filter(userName=username).order_by('deadlineDate', 'deadlineTime').values()
        
        # Retrieve all admins
        admins = TaskMate_userDetails.objects.filter(role='admin').values('username', 'fullName')

        # Check if an admin is selected
        selected_admin = request.GET.get('admin')  # Get the selected admin from the query parameters
        if selected_admin:
            # Retrieve tasks created by the selected admin
            admin_tasks = TaskMate_taskDetails.objects.filter(userName=selected_admin).order_by('deadlineDate', 'deadlineTime').values()
        else:
            admin_tasks = []  # No admin selected, so no tasks to show

        # Check for delete message and deleted task details
        delete_message = request.session.pop('delete_message', None)  # Get and remove the message from the session
        deleted_task = request.session.pop('deleted_task', None)  # Get and remove the deleted task details

        data['user_tasks'] = user_tasks
        data['admin_tasks'] = admin_tasks
        data['admins'] = admins
        data['selected_admin'] = selected_admin
        data['delete_message'] = delete_message  # Pass the message to the template
        data['deleted_task'] = deleted_task  # Pass the deleted task details to the template
        return render(request, 'userDashboard.html', data)
    else:
        return redirect('login')

def acceptTask(request, task_id):
    if request.method == 'POST':
        username = request.session['username']  # Get the username from the session
        
        # Update the task to indicate it has been accepted
        TaskMate_taskDetails.objects.filter(taskId=task_id).update(
            userName=username,
            status='In Progress',  # Set status to In Progress
            acceptedBy=username  # Store the name of the user who accepted the task
        )
        
        # Store a message in the session to indicate the task has been accepted
        request.session['accept_message'] = f"In Progress By {username}"
        
        # Check the user's role to determine where to redirect
        user = TaskMate_userDetails.objects.get(username=username)
        if user.role == 'admin':
            return redirect('homepage')  # Redirect to admin homepage
        else:
            return redirect('userDashboard')  # Redirect to user dashboard
    
def cancelTask(request, task_id):
    if request.method == 'POST':
        # Get the task to be canceled
        task = TaskMate_taskDetails.objects.filter(taskId=task_id).first()
        
        if task:
            # Update the task status to indicate it has been canceled
            task.status = 'Canceled'  # Change this to whatever status indicates it's available again
            task.acceptedBy = None  # Clear the acceptedBy field
            task.save()  # Save the changes

        return redirect('userDashboard')  # Redirect back to the user dashboard


def finishTask(request, task_id):
    if request.method == 'POST':
        # Logic for marking the task as finished
        task = TaskMate_taskDetails.objects.filter(taskId=task_id).first()
        if task:
            # Update the task status to 'Finished' or any other desired status
            task.status = 'Finished'
            task.save()  # Save the changes
            request.session['message'] = "Task marked as finished."
        return redirect('userDashboard')  # Redirect back to the user dashboard