from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import MessageForm
from .models import Conversation

User = get_user_model()


def _is_recruiter(user):
    return hasattr(user, "profile") and user.profile.is_recruiter


@login_required
def inbox(request):
    """List every conversation the logged-in user (recruiter or candidate) is part of."""
    conversations = (
        Conversation.objects.filter(Q(recruiter=request.user) | Q(candidate=request.user))
        .distinct()
        .order_by("-created_at")
    )

    rows = [
        {
            "conversation": c,
            "other": c.other_participant(request.user),
            "last_message": c.last_message(),
            "unread": c.unread_count_for(request.user),
        }
        for c in conversations
    ]
    return render(request, "messaging/inbox.html", {"rows": rows})


@login_required
def conversation_detail(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk)

    if request.user.pk not in (conversation.recruiter_id, conversation.candidate_id):
        raise PermissionDenied("You are not part of this conversation.")

    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.save()
            return redirect("messaging:conversation_detail", pk=conversation.pk)
    else:
        form = MessageForm()

    # Mark messages sent by the other participant as read now that this user has opened the thread.
    conversation.messages.exclude(sender=request.user).update(is_read=True)

    return render(
        request,
        "messaging/conversation_detail.html",
        {
            "conversation": conversation,
            "thread": conversation.messages.select_related("sender"),
            "other": conversation.other_participant(request.user),
            "form": form,
        },
    )


@login_required
def start_conversation(request, candidate_id):
    """Recruiter-only entry point: open an existing thread with a candidate, or create one."""
    if not _is_recruiter(request.user):
        raise PermissionDenied("Only recruiters can start a conversation with a candidate.")

    candidate = get_object_or_404(User, pk=candidate_id)

    conversation, _created = Conversation.objects.get_or_create(
        recruiter=request.user,
        candidate=candidate,
    )
    return redirect("messaging:conversation_detail", pk=conversation.pk)
