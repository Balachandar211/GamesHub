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

def promotional_email(context):
    return render_to_string("promotional.html", context=context)

def account_deletion_confirmation_email(context):
    return render_to_string("account_deletion_confirmation.html", context=context)

def validate_email_email(context):
    return render_to_string("validate_email.html", context=context)

def wallet_recharge_successful_email(context):
    return render_to_string("wallet_recharge_successful.html", context=context)

def ban_user_email(context):
    return render_to_string("ban_user.html", context=context)

def ban_user_deletion_email(context):
    return render_to_string("permanent_deletion_after_ban.html", context=context)

def ticket_resolution_email(context):
    return render_to_string("ticket_resolution.html", context=context)

def unblock_user_email(context):
    return render_to_string("unblock_user_confirmation.html", context=context)

def ticket_refund_email(context):
    return render_to_string("ticket_refund_success.html", context=context)