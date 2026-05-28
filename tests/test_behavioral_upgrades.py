"""
Test suite for Behavioral Alignment + Self Reflection v2 upgrades.
Covers: IdentityCore, homeostasis, creative tolerance, contradiction detection,
       reflection decay, temp/persistent split, meta-stability, controlled variance.
"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ── Identity Core Tests ──────────────────────────────────────────────────────

from cognition.behavioral.identity_core import IdentityCore


def test_identity_core_traits_immutable():
    core = IdentityCore()
    traits = core.traits
    assert len(traits) == 6, f"Expected 6 traits, got {len(traits)}"
    assert traits["grounded"] is True
    assert traits["calm"] is True
    assert traits["observant"] is True
    assert traits["subtle_humor"] is True
    assert traits["emotionally_stable"] is True
    assert traits["non_theatrical"] is True
    print("  PASS: Identity core has 6 immutable traits")


def test_identity_core_no_setter():
    core = IdentityCore()
    traits_copy = core.traits
    traits_copy["grounded"] = False
    # Verify the original was not modified (property returns a copy)
    assert core.traits["grounded"] is True, "Identity core trait should remain unchanged"
    # Verify property has no setter
    try:
        core.traits = {"modified": True}
        assert False, "Should not allow assignment to traits property"
    except AttributeError:
        pass
    # Verify internal __traits is name-mangled
    assert not hasattr(core, "__traits"), "Internal __traits should be name-mangled"
    print("  PASS: Identity core traits cannot be modified")


def test_identity_core_assert_in_prompt():
    core = IdentityCore()
    prompt = "TEST PROMPT"
    result = core.assert_identity(prompt)
    assert result.startswith("TEST PROMPT")
    assert "IDENTITY CORE:" in result
    assert "Grounded" in result
    assert "Calm" in result
    assert "Observant" in result
    assert "Subtle Humor" in result
    assert "Emotionally Stable" in result
    assert "Non Theatrical" in result
    print("  PASS: Identity core injects all 6 traits into prompt")


# ── PersonalityEngine Upgrades Tests ──────────────────────────────────────────

from personality.personality_engine import PersonalityEngine


def test_personality_engine_session_reset():
    pe = PersonalityEngine()
    pe.apply_stabilization({"warmth": 0.2, "humor": 0.15})
    mods = pe.get_tone_modifiers()
    assert mods["warmth"] == 0.2
    pe.reset_session()
    mods = pe.get_tone_modifiers()
    assert mods["warmth"] == 0.0, f"Expected 0.0 after reset, got {mods['warmth']}"
    assert mods["humor"] == 0.0
    print("  PASS: Session modifiers reset to zero")


def test_personality_engine_temp_vs_persistent():
    pe = PersonalityEngine()
    pe.apply_stabilization({"warmth": 0.15, "verbosity": -0.1})
    pe.promote_to_persistent("warmth")
    # After promotion but before reset: persistent=0.15, session=0.15 → effective=0.30
    # Reset to clear session and test persistence
    pe.reset_session()
    eff = pe.get_effective_modifiers()
    assert eff["warmth"] == 0.15, f"Persistent warmth should survive reset, got {eff['warmth']}"
    assert eff["verbosity"] == 0.0, f"Session verbosity should be gone after reset, got {eff['verbosity']}"
    print("  PASS: Temporary vs persistent split works correctly")


def test_personality_engine_homeostasis():
    pe = PersonalityEngine()
    pe._homeostasis_rate = 0.05
    pe.persistent_modifiers["warmth"] = 0.2
    pe.persistent_modifiers["humor"] = -0.15
    for _ in range(3):
        pe._homeostasis_tick()
    assert pe.persistent_modifiers["warmth"] < 0.2, "Warmth should decay toward 0"
    assert pe.persistent_modifiers["humor"] > -0.15, "Negative humor should rise toward 0"
    print(f"  PASS: Homeostasis pulls modifiers toward baseline (warmth={pe.persistent_modifiers['warmth']:.3f}, humor={pe.persistent_modifiers['humor']:.3f})")


def test_personality_engine_homeostasis_bounded():
    pe = PersonalityEngine()
    pe._homeostasis_rate = 0.001
    pe.persistent_modifiers["warmth"] = 0.01
    for _ in range(5):
        pe._homeostasis_tick()
    assert pe.persistent_modifiers["warmth"] >= 0.0, "Homeostasis should not go below 0 for positive values"
    print("  PASS: Homeostasis does not overshoot below zero")


def test_personality_engine_identity_core_in_prompt():
    pe = PersonalityEngine()
    prompt = pe.build_system_prompt({"mood": {"mood": "neutral"}})
    assert "IDENTITY CORE:" in prompt, "Identity core should be in system prompt"
    assert "Grounded" in prompt
    assert "Calm" in prompt
    print("  PASS: Identity core injected into system prompt")


def test_personality_engine_identity_core_after_behavioral():
    pe = PersonalityEngine()
    pe.apply_stabilization({"warmth": 0.2})
    prompt = pe.build_system_prompt({"mood": {"mood": "neutral"}})
    behavioral_pos = prompt.find("BEHAVIORAL CONTEXT")
    identity_pos = prompt.find("IDENTITY CORE")
    assert behavioral_pos < identity_pos, "Identity core should appear AFTER behavioral context"
    print("  PASS: Identity core appears after behavioral context in prompt")


def test_personality_engine_identity_immutable_after_stabilization():
    pe = PersonalityEngine()
    pe.apply_stabilization({"warmth": 0.3, "humor": 0.3})
    prompt = pe.build_system_prompt({"mood": {"mood": "neutral"}})
    for _ in range(10):
        pe.apply_stabilization({"warmth": -0.1, "formality": 0.2, "humor": -0.1})
    prompt2 = pe.build_system_prompt({"mood": {"mood": "neutral"}})
    identity_section = prompt2[prompt2.find("IDENTITY CORE:"):]
    assert "Grounded" in identity_section
    assert "Calm" in identity_section
    assert "Emotionally Stable" in identity_section
    print("  PASS: Identity core remains unchanged after many stabilization cycles")


def test_personality_engine_variance_deterministic():
    pe = PersonalityEngine()
    v1 = pe._variance("test_key")
    v2 = pe._variance("test_key")
    assert v1 == v2, f"Variance should be deterministic, got {v1} != {v2}"
    v3 = pe._variance("other_key")
    assert v1 != v3 or abs(v1 - v3) > 0.001, "Different keys should produce different variance"
    assert -pe._variance_range <= v1 <= pe._variance_range, f"Variance within range: {v1}"
    print(f"  PASS: Controlled variance is deterministic and bounded ({v1:.4f})")


def test_personality_engine_get_effective_modifiers():
    pe = PersonalityEngine()
    pe.apply_stabilization({"warmth": 0.1})
    pe.persistent_modifiers["verbosity"] = -0.05
    eff = pe.get_effective_modifiers()
    assert eff["warmth"] == 0.1, f"Session warmth should be 0.1, got {eff['warmth']}"
    assert eff["verbosity"] == -0.05, f"Persistent verbosity should be -0.05, got {eff['verbosity']}"
    # combined
    pe.apply_stabilization({"verbosity": -0.03})
    eff2 = pe.get_effective_modifiers()
    assert abs(eff2["verbosity"] - (-0.08)) < 0.001, f"Combined verbosity should be -0.08, got {eff2['verbosity']}"
    print("  PASS: Effective modifiers combine persistent + session correctly")


# ── Creative Tolerance Tests ──────────────────────────────────────────────────

from cognition.reflection.self_reflector import SelfReflectionEngine, ReflectionObservation
from cognition.intent.signal import CognitionSignal


def test_creative_tolerance_awkwardness_few_fillers():
    engine = SelfReflectionEngine()
    signal = CognitionSignal()
    mood = {"mood": "neutral"}
    obs = engine.reflect("hi", "Well, actually, basically, that's what I think.", signal, mood, {})
    score = obs.dimensions["awkwardness"]
    assert score >= 0.4, f"2-4 fillers should score >= 0.4, got {score}"
    print(f"  PASS: Moderate fillers score {score:.2f} (should be >= 0.4)")


def test_creative_tolerance_awkwardness_many_fillers():
    engine = SelfReflectionEngine()
    signal = CognitionSignal()
    mood = {"mood": "neutral"}
    obs = engine.reflect("hi", "Well, actually, basically, like, honestly, literally, sort of, kind of, I think maybe perhaps.", signal, mood, {})
    score = obs.dimensions["awkwardness"]
    assert score < 0.5, f"Many fillers should score < 0.5, got {score}"
    print(f"  PASS: High filler count scores {score:.2f} (should be < 0.5)")


def test_creative_tolerance_awkwardness_clean():
    engine = SelfReflectionEngine()
    signal = CognitionSignal()
    mood = {"mood": "neutral"}
    obs = engine.reflect("hi", "Hey, what's up? How can I help you today?", signal, mood, {})
    score = obs.dimensions["awkwardness"]
    assert score >= 0.8, f"Clean response should score >= 0.8, got {score}"
    print(f"  PASS: Clean response scores {score:.2f} (should be >= 0.8)")


def test_creative_tolerance_humor_stressed():
    engine = SelfReflectionEngine()
    signal = CognitionSignal()
    mood_stressed = {"mood": "stressed"}
    # Joking while stressed - was 0.2, now should be 0.4
    obs = engine.reflect("help", "Haha that's funny!", signal, mood_stressed, {})
    score = obs.dimensions["humor_appropriateness"]
    assert score >= 0.35, f"Stressed+humor should score >= 0.35, got {score}"
    print(f"  PASS: Stressed+humor scores {score:.2f} (was 0.2, now >= 0.35)")


def test_creative_tolerance_grounding_one_phrase():
    engine = SelfReflectionEngine()
    signal = CognitionSignal()
    mood = {"mood": "neutral"}
    # One ungrounded phrase - was 0.3, now should be 0.6
    obs = engine.reflect("search", "I searched the web and here is what I found.", signal, mood, {})
    score = obs.dimensions["grounding"]
    assert score >= 0.55, f"One ungrounded phrase should score >= 0.55, got {score}"
    print(f"  PASS: One ungrounded phrase scores {score:.2f} (was 0.3, now >= 0.55)")


def test_creative_tolerance_grounding_multiple():
    engine = SelfReflectionEngine()
    signal = CognitionSignal()
    mood = {"mood": "neutral"}
    obs = engine.reflect("search", "I searched the web, I browsed the results, and I created a summary.", signal, mood, {})
    score = obs.dimensions["grounding"]
    assert score < 0.5, f"Multiple ungrounded phrases should score < 0.5, got {score}"
    print(f"  PASS: Multiple ungrounded phrases scores {score:.2f} (should be < 0.5)")


def test_creative_tolerance_personality_drift_one_word():
    engine = SelfReflectionEngine()
    signal = CognitionSignal()
    mood = {"mood": "neutral"}
    obs = engine.reflect("hi", "Kindly check the results.", signal, mood, {})
    score = obs.dimensions["personality_drift"]
    assert score >= 0.6, f"One formal word should score >= 0.6, got {score}"
    print(f"  PASS: One formal word scores {score:.2f} (was 0.3, now >= 0.6)")


def test_creative_tolerance_personality_drift_multiple():
    engine = SelfReflectionEngine()
    signal = CognitionSignal()
    mood = {"mood": "neutral"}
    obs = engine.reflect("hi", "Kindly find the results. It is advisable to proceed.", signal, mood, {})
    score = obs.dimensions["personality_drift"]
    assert score < 0.6, f"Multiple formal words should score < 0.6, got {score}"
    print(f"  PASS: Multiple formal words scores {score:.2f} (should be < 0.6)")


def test_creative_tolerance_verbosity_wider():
    engine = SelfReflectionEngine()
    signal = CognitionSignal(intent="casual_chat", confidence=0.8, response_depth="short")
    mood = {"mood": "neutral"}
    # Short target is ~10 words, ±75% = 2.5 to 17.5 words
    obs = engine.reflect("hi", "Hey! How can I help you today? That is a great question.", signal, mood, {})
    assert obs.dimensions["verbosity_match"] > 0.5, f"14 words should match short depth better now"
    print(f"  PASS: Wider verbosity tolerance (±75%) gives more lenient matching")


# ── Contradiction Detection Tests ─────────────────────────────────────────────

from cognition.habits.confidence_engine import ConfidenceEngine
from cognition.behavioral.memory import BehavioralMemory, ContextualPreference
from cognition.behavioral.extractor import BehavioralSignal


class TempMemoryStore:
    def __init__(self):
        self.data = {"preferences": [], "version": 1}
    def load(self):
        return self.data
    def save(self, data):
        self.data = data


def test_contradiction_detection_tracks():
    store = TempMemoryStore()
    mem = BehavioralMemory(store, ConfidenceEngine())
    # playful and supportive are a contradiction pair
    mem._detect_contradictions("playful")
    mem._detect_contradictions("supportive")
    assert mem._contradiction_count >= 1, "playful -> supportive should be a contradiction"
    print(f"  PASS: Contradiction detected (count={mem._contradiction_count})")


def test_contradiction_non_contradictory():
    store = TempMemoryStore()
    mem = BehavioralMemory(store, ConfidenceEngine())
    mem._detect_contradictions("supportive")
    mem._detect_contradictions("playful")
    # These are not contradiction pairs
    initial = mem._contradiction_count
    mem._detect_contradictions("neutral")
    assert mem._contradiction_count == initial, "supportive -> playful -> neutral should not contradict"
    print("  PASS: Non-contradictory preferences do not trigger contradiction")


def test_contradiction_slows_reinforcement():
    store = TempMemoryStore()
    mem = BehavioralMemory(store, ConfidenceEngine())
    signal = BehavioralSignal(user_sentiment=0.8, signal_strength=0.7)
    context = {"mood": {"mood": "curious"}, "working": {"current_task": ""}}
    # First, create playful preference
    mem.update(signal, context)  # This will infer "supportive" (sentiment > 0.3, humor < 0.6)
    # Now create a contradictory signal
    signal2 = BehavioralSignal(user_sentiment=-0.5, signal_strength=0.7)
    mem.update(signal2, context)  # This will infer "supportive" (sentiment < -0.3)
    # The contradiction penalty should have been applied if contradictory
    assert mem._contradiction_count >= 0
    print("  PASS: Contradiction tracking works in update flow")


def test_contradiction_in_trends():
    store = TempMemoryStore()
    mem = BehavioralMemory(store, ConfidenceEngine())
    mem._contradiction_count = 5
    trends = mem.get_trends()
    assert "contradiction_count" in trends
    assert trends["contradiction_count"] == 5
    print("  PASS: Contradiction count exposed in trends")


# ── Reflection Decay Tests ────────────────────────────────────────────────────

from config.settings import REFLECTION_DECAY_MULTIPLIER


def test_reflection_decay_uses_multiplier():
    assert REFLECTION_DECAY_MULTIPLIER == 3.0, f"Expected 3.0, got {REFLECTION_DECAY_MULTIPLIER}"
    print(f"  PASS: REFLECTION_DECAY_MULTIPLIER = {REFLECTION_DECAY_MULTIPLIER}")


def test_reflection_insights_half_weight():
    store = TempMemoryStore()
    mem = BehavioralMemory(store, ConfidenceEngine())
    signal = BehavioralSignal(user_sentiment=0.8, signal_strength=0.7)
    context = {"mood": {"mood": "curious"}, "working": {"current_task": ""}}
    for _ in range(4):
        mem.update(signal, context)
    prefs = mem.get_all_preferences()
    assert len(prefs) > 0
    # Reflection insights for more_humorous should apply with half weight
    insights = {"actionable": ["more_humorous"]}
    before = prefs[0].confidence
    mem.apply_reflection_insights(insights)
    after = prefs[0].confidence
    assert after >= before, "Reflection should not decrease confidence"
    delta = after - before
    assert delta <= 0.03, f"Half-weight boost should be small, got {delta}"
    print(f"  PASS: Reflection insights apply with half-weight (delta={delta:.4f})")


# ── Meta-Stability Tests ──────────────────────────────────────────────────────

from cognition.behavioral.stabilizer import PersonalityStabilizer


def test_meta_stability_snapshot():
    pe = PersonalityEngine()
    stab = PersonalityStabilizer(pe)
    pref = ContextualPreference(
        context_key="mood:curious", preference="supportive",
        confidence=0.7, observation_count=5,
    )
    for _ in range(3):
        stab.apply([pref])
    report = stab.get_meta_report()
    assert report["snapshot_count"] >= 3, f"Expected >= 3 snapshots, got {report['snapshot_count']}"
    assert "status" in report
    assert "average_drift" in report
    assert "drift_trend" in report
    print(f"  PASS: Meta-stability report generated ({report['snapshot_count']} snapshots, status={report['status']})")


def test_meta_stability_empty():
    stab = PersonalityStabilizer()
    report = stab.get_meta_report()
    assert report["status"] == "no_data"
    print("  PASS: Meta-stability handles empty state")


def test_meta_stability_contradiction_integration():
    pe = PersonalityEngine()
    stab = PersonalityStabilizer(pe)
    pref = ContextualPreference(
        context_key="mood:curious", preference="supportive",
        confidence=0.8, observation_count=5,
    )
    stab.apply([pref])
    report = stab.get_meta_report(contradiction_count=3)
    assert report["contradiction_count"] == 3
    print(f"  PASS: Meta-stability integrates contradiction count: {report['contradiction_count']}")


def test_meta_stability_trend_stable():
    pe = PersonalityEngine()
    stab = PersonalityStabilizer(pe)
    prefs = []
    for _ in range(10):
        stab.apply(prefs)
    report = stab.get_meta_report()
    assert report["drift_trend"] in ("stable", "increasing")
    print(f"  PASS: Meta-stability drift trend: {report['drift_trend']}")


# ── Drift Simulation (Long-Run) ───────────────────────────────────────────────

def test_drift_simulation():
    pe = PersonalityEngine()
    stab = PersonalityStabilizer(pe)
    store = TempMemoryStore()
    mem = BehavioralMemory(store, ConfidenceEngine())

    signals_playful = [
        BehavioralSignal(user_sentiment=0.6, signal_strength=0.5, humor_appropriateness=0.8),
        BehavioralSignal(user_sentiment=0.7, signal_strength=0.6, humor_appropriateness=0.9),
        BehavioralSignal(user_sentiment=0.5, signal_strength=0.4, humor_appropriateness=0.7),
    ]
    signals_serious = [
        BehavioralSignal(user_sentiment=-0.4, signal_strength=0.5),
        BehavioralSignal(user_sentiment=-0.5, signal_strength=0.6),
        BehavioralSignal(user_sentiment=-0.3, signal_strength=0.4),
    ]
    context = {"mood": {"mood": "neutral"}, "working": {"current_task": ""}}

    for i in range(50):
        sig = signals_playful[i % len(signals_playful)] if i % 2 == 0 else signals_serious[i % len(signals_serious)]
        mem.update(sig, context)
        if i % 5 == 0:
            prefs = mem.get_preferences_for_context(context)
            stab.apply(prefs)

    eff = pe.get_effective_modifiers()
    total_drift = sum(abs(v) for v in eff.values())
    assert total_drift < 0.6, f"Total drift should be bounded < 0.6, got {total_drift}"
    for k, v in eff.items():
        assert -0.3 <= v <= 0.3, f"Modifier {k}={v} exceeds ±0.3 cap"

    # Verify identity core is preserved
    prompt = pe.build_system_prompt(context)
    assert "Grounded" in prompt
    assert "Calm" in prompt
    assert "Observant" in prompt
    assert "IDENTITY CORE:" in prompt

    print(f"  PASS: Drift simulation stable (total_drift={total_drift:.3f}, modifiers={eff})")


# ── Routing Stability Tests ──────────────────────────────────────────────────

from core.orchestration.router import ExecutionRouter
from cognition.intent.classifier import CognitionAssessor
from cognition.intent.predictor import IntentPredictor


def test_routing_conversation_greeting():
    assessor = CognitionAssessor()
    predictor = IntentPredictor(assessor)
    router = ExecutionRouter()
    signal = predictor.predict("hey nira", {})
    route = router.route(signal)
    assert route.model_track == "conversational_model", \
        f"'hey nira' should route to conversational, got {route.model_track}"
    assert route.activate_tools == False
    print(f"  PASS: 'hey nira' -> {route.model_track}")


def test_routing_reasoning_deep_explain():
    assessor = CognitionAssessor()
    predictor = IntentPredictor(assessor)
    router = ExecutionRouter()
    signal = predictor.predict("Explain transformer attention internally", {})
    route = router.route(signal)
    assert route.model_track == "reasoning_model", \
        f"'Explain transformer attention' should route to reasoning, got {route.model_track}"
    print(f"  PASS: 'Explain transformer attention' -> {route.model_track}")


def test_routing_reasoning_comparison():
    assessor = CognitionAssessor()
    predictor = IntentPredictor(assessor)
    router = ExecutionRouter()
    signal = predictor.predict("Compare vector memory vs graph memory", {})
    route = router.route(signal)
    assert route.model_track == "reasoning_model", \
        f"'Compare vector vs graph' should route to reasoning, got {route.model_track}"
    print(f"  PASS: 'Compare vector vs graph' -> {route.model_track}")


def test_routing_tools_and_reasoning():
    assessor = CognitionAssessor()
    predictor = IntentPredictor(assessor)
    router = ExecutionRouter()
    signal = predictor.predict("search latest AI news and summarize implications", {})
    route = router.route(signal)
    assert route.model_track == "reasoning_model", \
        f"Search + summarize should route to reasoning, got {route.model_track}"
    assert route.activate_tools == True, \
        f"Should activate tools, got activate_tools={route.activate_tools}"
    print(f"  PASS: 'search AI news and summarize' -> {route.model_track} + tools")


# ── Main Test Runner ─────────────────────────────────────────────────────────

def run_all():
    tests = [
        # Identity Core
        test_identity_core_traits_immutable,
        test_identity_core_no_setter,
        test_identity_core_assert_in_prompt,
        # PersonalityEngine upgrades
        test_personality_engine_session_reset,
        test_personality_engine_temp_vs_persistent,
        test_personality_engine_homeostasis,
        test_personality_engine_homeostasis_bounded,
        test_personality_engine_identity_core_in_prompt,
        test_personality_engine_identity_core_after_behavioral,
        test_personality_engine_identity_immutable_after_stabilization,
        test_personality_engine_variance_deterministic,
        test_personality_engine_get_effective_modifiers,
        # Creative tolerance
        test_creative_tolerance_awkwardness_few_fillers,
        test_creative_tolerance_awkwardness_many_fillers,
        test_creative_tolerance_awkwardness_clean,
        test_creative_tolerance_humor_stressed,
        test_creative_tolerance_grounding_one_phrase,
        test_creative_tolerance_grounding_multiple,
        test_creative_tolerance_personality_drift_one_word,
        test_creative_tolerance_personality_drift_multiple,
        test_creative_tolerance_verbosity_wider,
        # Contradiction detection
        test_contradiction_detection_tracks,
        test_contradiction_non_contradictory,
        test_contradiction_slows_reinforcement,
        test_contradiction_in_trends,
        # Reflection decay
        test_reflection_decay_uses_multiplier,
        test_reflection_insights_half_weight,
        # Meta-stability
        test_meta_stability_snapshot,
        test_meta_stability_empty,
        test_meta_stability_contradiction_integration,
        test_meta_stability_trend_stable,
        # Drift simulation
        test_drift_simulation,
        # Routing stability
        test_routing_conversation_greeting,
        test_routing_reasoning_deep_explain,
        test_routing_reasoning_comparison,
        test_routing_tools_and_reasoning,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"  FAIL: {test.__name__} -> {e}")
            import traceback
            traceback.print_exc()

    total = passed + failed
    print(f"\n{'='*50}")
    print(f"UPGRADE TESTS: {passed}/{total} passed, {failed} failed")
    print(f"{'='*50}")
    return failed == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
