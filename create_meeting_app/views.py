from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.management import call_command
from .models import Meeting
from .forms import CreateMeetingForm, JoinMeetingForm


def dashboard(request):
    meetings = Meeting.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'dashboard.html', {'meetings': meetings})

def create_meeting(request):
    if request.method == 'POST':
        form = CreateMeetingForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.user = request.user
            meeting.save()
            messages.success(request, 'Meeting created successfully!')
            return redirect('dashboard')
        messages.error(request, 'Error creating meeting. Please check the form.')
    return redirect('dashboard')

def join_meeting(request):
    if request.method == 'POST':
        form = JoinMeetingForm(request.POST)
        if form.is_valid():
            meeting = get_object_or_404(Meeting, pk=form.cleaned_data['meeting_id'], user=request.user)
            meeting.meeting_link = form.cleaned_data['meeting_link']
            meeting.join_time = form.cleaned_data['join_time']
            meeting.joined = False  # reset so scheduler will pick it up
            meeting.save()
            messages.success(request, 'Meeting details saved! Bot will join on time.')
            return redirect('meeting_page', meeting_id=meeting.pk)
        messages.error(request, 'Error saving meeting details.')
    return redirect('dashboard')

def meeting_page(request, meeting_id):
    meeting = get_object_or_404(Meeting, pk=meeting_id)

    segments = []
    for transcript in meeting.transcripts.order_by('created'):
        # Each transcript.text has multi speaker segments separated by double newlines
        blocks = transcript.text.split('\n\n')
        for block in blocks:
            if ': ' in block:
                speaker, text = block.split(': ', 1)
            else:
                speaker, text = None, block
            segments.append({
                'speaker': speaker,
                'text': text,
                'created': transcript.created,
            })

    screenshots = meeting.screenshots.order_by('created')

    return render(request, 'meeting_detail.html', {
        'meeting': meeting,
        'segments': segments,
        'screenshots': screenshots,
    })

@require_POST
def delete_meeting(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id, user=request.user)
    meeting.delete()
    return JsonResponse({'status': 'success'})

@csrf_exempt
def transcribe_meeting_view(request, meeting_id):
    if request.method == 'POST':
        call_command('transcribe_meeting', str(meeting_id))
        return redirect('meeting_page', meeting_id=meeting_id)
    return HttpResponse("Invalid request", status=400)
