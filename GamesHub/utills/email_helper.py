from django.template.loader import render_to_string

def signup_email(context):
    return render_to_string("signup.html", context=context)

def forgot_password_email(context):
    return render_to_string("forgot_password.html", context=context)

def password_change_success_email(context):
    return render_to_string("password_change_successful.html", context=context)

def recover_account_email(context):
    return render_to_string("recover_account.html", context=context)

def account_recovery_success_email(context):
    return render_to_string("account_recovery_successful.html", context=context)

def user_deletion_email(context):
    return render_to_string("user_deletion.html", context=context)

def user_deletion_confirmation(context):
    return render_to_string("deletion_confirmation.html", context=context)

def recoverable_deletion_confirmation(context):
    return render_to_string("recoverable_deletion.html", context=context)

def game_bought_details(context):
    return render_to_string("games_bought_details.html", context=context)
