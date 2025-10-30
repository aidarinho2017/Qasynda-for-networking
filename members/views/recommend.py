# members/views/recommend.py
import json
import os
import re
from openai import OpenAI
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from ..models import Event, Recommendation

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def recommend_events(request):
    user = request.user
    profile = getattr(user, 'profile', None)
    interests = profile.interests if profile and profile.interests else request.data.get('interest', '')

    events = Event.objects.all()
    if not events.exists():
        return Response({"detail": "No events available."}, status=400)

    events_text = "\n".join([f"{e.id}. {e.title} — {e.category} — {e.address}" for e in events])

    prompt = f"""
You are an assistant that recommends events for a user.

User interests: {interests}

Events:
{events_text}

Task:
Pick top 3 events best matching the user's interests. Output strictly valid JSON array.
"""

    completion = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=500

    )
    ai_text = completion.choices[0].message.content.strip()

    try:
        recs = json.loads(ai_text)
    except:
        match = re.search(r'(\[.*\])', ai_text, flags=re.S)
        if match:
            recs = json.loads(match.group(1))
        else:
            return Response({"error": "AI returned invalid JSON", "raw": ai_text}, status=500)

    saved = []
    for rec in recs:
        event_id = rec.get('event_id')
        reason = rec.get('reason', '')
        if not event_id:
            continue
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            continue

        recommendation = Recommendation.objects.create(
            event=event,
            interest=interests,
            reason=reason
        )
        saved.append({
            "id": recommendation.id,
            "event_id": event.id,
            "event_title": event.title,
            "reason": recommendation.reason,
            "created_at": recommendation.created_at
        })

    return Response({"saved_recommendations": saved})
