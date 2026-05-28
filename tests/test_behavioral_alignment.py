"""
Comprehensive test suite for Behavioral Alignment + Self Reflection Cognitive Layer.

Tests: BehavioralSignalExtractor, BehavioralMemory, ContextualReinforcer,
       PersonalityStabilizer, SelfReflectionEngine, ReflectionMemory.

Also validates that routing is NOT changed by the new layer.
"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ── Behavioral Signal Extractor Tests ────────────────────────────────────────

from cognition.behavioral.extractor import BehavioralSignalExtractor, BehavioralSignal


def test_extractor_positive_reaction():
    ext = BehavioralSignalExtractor()
    signal = ext.extract("thanks that works perfectly", "Here is the code.", {})
    assert signal.user_sentiment > 0.3, f"Expected positive sentiment, got {signal.user_sentiment}"
    assert signal.signal_strength > 0.0
    print("  PASS: Positive reaction detected")


def test_extractor_negative_reaction():
    ext = BehavioralSignalExtractor()
    signal = ext.extract("no that's wrong", "Here is the code.", {})
    assert signal.user_sentiment < -0.3, f"Expected negative sentiment, got {signal.user_sentiment}"
    print("  PASS: Negative reaction detected")


def test_extractor_correction():
    ext = BehavioralSignalExtractor()
    signal = ext.extract("no, actually i meant the other thing", "Here is the answer.", {})
    assert signal.user_sentiment < 0, f"Expected correction sentiment < 0"
    print("  PASS: Correction signal detected")


def test_extractor_follow_up():
    ext = BehavioralSignalExtractor()
    signal = ext.extract("also what about memory systems?", "Here is the answer about vectors.", {})
    assert signal.signal_strength > 0.2, f"Expected follow-up strength > 0.2"
    print("  PASS: Follow-up signal detected")


def test_extractor_empty_input():
    ext = BehavioralSignalExtractor()
    signal = ext.extract("", "Some response.", {})
    assert signal.signal_strength == 0.0
    print("  PASS: Empty input handled safely")


def test_extractor_hinglish_reaction():
    ext = BehavioralSignalExtractor()
    signal = ext.extract("sahi hai, kaam kar raha thanks", "Yeh code kaam karega.", {})
    assert signal.user_sentiment >= 0
    print("  PASS: Hinglish reaction handled")


def test_extractor_no_previous_response():
    ext = BehavioralSignalExtractor()
    signal = ext.extract("hello", "", {})
    assert signal.signal_strength < 0.3, "No previous response should dampen signal"
    print("  PASS: No previous response dampens signal correctly")


# ── BehavioralMemory Tests ───────────────────────────────────────────────────

from cognition.habits.confidence_engine import ConfidenceEngine
from cognition.behavioral.memory import BehavioralMemory, ContextualPreference


class TempMemoryStore:
    def __init__(self):
        self.data = {"preferences": [], "version": 1}

    def load(self):
        return self.data

    def save(self, data):
        self.data = data


def test_memory_update_and_retrieve():
    store = TempMemoryStore()
    mem = BehavioralMemory(store, ConfidenceEngine())
    signal = BehavioralSignal(user_sentiment=0.8, signal_strength=0.7)
    context = {"mood": {"mood": "curious"}, "working": {"current_task": ""}}

    mem.update(signal, context)
    prefs = mem.get_all_preferences()
    assert len(prefs) == 1, f"Expected 1 preference, got {len(prefs)}"
    assert prefs[0].observation_count == 1
    assert prefs[0].confidence > 0.0
    print("  PASS: Preference created on update")


def test_memory_confidence_grows():
    store = TempMemoryStore()
    mem = BehavioralMemory(store, ConfidenceEngine())
    signal = BehavioralSignal(user_sentiment=0.8, signal_strength=0.7)
    context = {"mood": {"mood": "curious"}, "working": {"current_task": ""}}

    for _ in range(5):
        mem.update(signal, context)

    prefs = mem.get_all_preferences()
    assert len(prefs) == 1
    assert prefs[0].observation_count == 5
    assert prefs[0].confidence > 0.1
    print(f"  PASS: Confidence grows with observations ({prefs[0].confidence})")


def test_memory_context_key_differentiation():
    store = TempMemoryStore()
    mem = BehavioralMemory(store, ConfidenceEngine())
    signal = BehavioralSignal(user_sentiment=0.8, signal_strength=0.7)

    ctx_stressed = {"mood": {"mood": "stressed"}, "working": {"current_task": ""}}
    ctx_playful = {"mood": {"mood": "playful"}, "working": {"current_task": ""}}

    mem.update(signal, ctx_stressed)
    mem.update(signal, ctx_playful)

    prefs = mem.get_all_preferences()
    assert len(prefs) == 2, f"Expected 2 context keys, got {len(prefs)}"
    keys = [p.context_key for p in prefs]
    assert any("mood:stressed" in k for k in keys)
    assert any("mood:playful" in k for k in keys)
    print("  PASS: Different context keys created")


def test_memory_cap_at_09():
    store = TempMemoryStore()
    mem = BehavioralMemory(store, ConfidenceEngine())
    signal = BehavioralSignal(user_sentiment=0.9, signal_strength=0.9)
    context = {"mood": {"mood": "focused"}, "working": {"current_task": ""}}

    for _ in range(100):
        mem.update(signal, context)

    prefs = mem.get_all_preferences()
    assert prefs[0].confidence <= 0.9, f"Confidence capped at 0.9, got {prefs[0].confidence}"
    print(f"  PASS: Confidence capped at 0.9 (got {prefs[0].confidence})")


def test_memory_min_observations():
    store = TempMemoryStore()
    mem = BehavioralMemory(store, ConfidenceEngine())
    signal = BehavioralSignal(user_sentiment=0.5, signal_strength=0.3)
    context = {"mood": {"mood": "neutral"}, "working": {"current_task": ""}}

    mem.update(signal, context)
    prefs = mem.get_preferences_for_context(context)
    assert len(prefs) == 0, "New preference should not be active yet (min_observations=3)"
    print("  PASS: Min observations gate works")


def test_memory_decay():
    store = TempMemoryStore()
    mem = BehavioralMemory(store, ConfidenceEngine())
    signal = BehavioralSignal(user_sentiment=0.8, signal_strength=0.7)
    context = {"mood": {"mood": "curious"}, "working": {"current_task": ""}}

    for _ in range(4):
        mem.update(signal, context)

    prefs = mem.get_all_preferences()
    before = prefs[0].confidence
    mem.decay()
    prefs = mem.get_all_preferences()
    after = prefs[0].confidence
    assert after <= before, f"Decay should reduce or keep confidence ({before} -> {after})"
    print(f"  PASS: Decay works ({before} -> {after})")


def test_memory_serialization_roundtrip():
    store = TempMemoryStore()
    mem = BehavioralMemory(store, ConfidenceEngine())
    signal = BehavioralSignal(user_sentiment=0.7, signal_strength=0.6)
    context = {"mood": {"mood": "curious"}, "working": {"current_task": ""}}
    mem.update(signal, context)

    saved = store.data
    assert "preferences" in saved
    assert len(saved["preferences"]) == 1

    mem2 = BehavioralMemory(store, ConfidenceEngine())
    assert len(mem2.get_all_preferences()) == 1
    print("  PASS: Serialization roundtrip preserves data")


def test_memory_apply_reflection_insights():
    store = TempMemoryStore()
    mem = BehavioralMemory(store, ConfidenceEngine())
    signal = BehavioralSignal(user_sentiment=0.8, signal_strength=0.7)
    context = {"mood": {"mood": "curious"}, "working": {"current_task": ""}}

    for _ in range(4):
        mem.update(signal, context)

    insights = {"actionable": ["reduce_verbosity"]}
    mem.apply_reflection_insights(insights)
    print("  PASS: Reflection insights applied without error")


# ── ContextualReinforcer Tests ───────────────────────────────────────────────

from cognition.behavioral.reinforcer import ContextualReinforcer


def test_reinforcer_zero_signal():
    ce = ConfidenceEngine()
    rein = ContextualReinforcer(ce)
    delta = rein.compute_reinforcement(0.0, 0.5)
    assert delta == 0.0
    print("  PASS: Zero signal -> zero reinforcement")


def test_reinforcer_positive_signal():
    ce = ConfidenceEngine()
    rein = ContextualReinforcer(ce)
    delta = rein.compute_reinforcement(0.8, 0.0)
    assert delta > 0.0
    print(f"  PASS: Positive signal gives delta={delta}")


def test_reinforcer_saturation():
    ce = ConfidenceEngine()
    rein = ContextualReinforcer(ce)
    delta = rein.compute_reinforcement(0.9, 0.95)
    assert delta < 0.02, f"Near-saturated confidence should give tiny delta, got {delta}"
    print(f"  PASS: Saturation dampening works (delta={delta})")


# ── PersonalityStabilizer Tests ───────────────────────────────────────────────

from cognition.behavioral.stabilizer import PersonalityStabilizer
from personality.personality_engine import PersonalityEngine


def test_stabilizer_no_preferences():
    pe = PersonalityEngine()
    stab = PersonalityStabilizer(pe)
    adjustments = stab.compute_personality_adjustments([])
    assert all(v == 0.0 for v in adjustments.values())
    print("  PASS: No preferences -> zero adjustments")


def test_stabilizer_single_preference():
    pe = PersonalityEngine()
    stab = PersonalityStabilizer(pe)
    pref = ContextualPreference(
        context_key="mood:curious", preference="supportive",
        confidence=0.8, observation_count=5,
    )
    adjustments = stab.compute_personality_adjustments([pref])
    assert adjustments["warmth"] > 0.0, f"Expected warmth > 0, got {adjustments}"
    assert adjustments["verbosity"] == 0.0
    print(f"  PASS: Supportive preference -> warmth={adjustments['warmth']}")


def test_stabilizer_caps():
    pe = PersonalityEngine()
    stab = PersonalityStabilizer(pe)
    prefs = [
        ContextualPreference(context_key="a", preference="supportive", confidence=0.9, observation_count=10),
        ContextualPreference(context_key="b", preference="playful", confidence=0.9, observation_count=10),
    ]
    adjustments = stab.compute_personality_adjustments(prefs)
    for k, v in adjustments.items():
        assert -0.3 <= v <= 0.3, f"Adjustment {k}={v} exceeds cap ±0.3"
    print(f"  PASS: All adjustments within caps: {adjustments}")


def test_stabilizer_apply():
    pe = PersonalityEngine()
    stab = PersonalityStabilizer(pe)
    pref = ContextualPreference(
        context_key="mood:curious", preference="concise",
        confidence=0.7, observation_count=5,
    )
    stab.apply([pref])
    modifiers = pe.get_tone_modifiers()
    assert modifiers["verbosity"] <= 0, "Concise preference should reduce verbosity"
    print(f"  PASS: Apply modifies engine: {modifiers}")


def test_stabilizer_drift_reset():
    pe = PersonalityEngine()
    pe.apply_stabilization({"warmth": 0.3, "verbosity": 0.3, "humor": 0.3, "formality": 0.0})
    stab = PersonalityStabilizer(pe)
    adjustments = stab.stabilize({"warmth": 0.3, "verbosity": 0.3, "humor": 0.3, "formality": 0.0})
    assert all(v == 0.0 for v in adjustments.values()), "Total drift > 0.8 should reset"
    print("  PASS: Drift reset works (total > 0.8 -> zero adjustments)")


# ── SelfReflectionEngine Tests ───────────────────────────────────────────────

from cognition.reflection.self_reflector import SelfReflectionEngine, ReflectionObservation
from cognition.intent.signal import CognitionSignal


def test_reflector_all_dimensions():
    engine = SelfReflectionEngine()
    signal = CognitionSignal(intent="casual_chat", confidence=0.8, response_depth="short")
    mood = {"mood": "neutral", "confidence": 0.5}
    obs = engine.reflect("hello", "Hey! How can I help?", signal, mood, {})

    assert len(obs.dimensions) == 9, f"Expected 9 dimensions, got {len(obs.dimensions)}"
    for dim, score in obs.dimensions.items():
        assert 0.0 <= score <= 1.0, f"Dimension {dim} score {score} out of range"
    print(f"  PASS: All 9 dimensions present and in range: {obs.dimensions}")


def test_reflector_coherence():
    engine = SelfReflectionEngine()
    signal = CognitionSignal()
    mood = {"mood": "neutral"}

    incoherent = engine.reflect("hi", "a a a a a a a a a a. a a a a a a a a. a a a a a.", signal, mood, {})
    coherent = engine.reflect("hi", "That is a well-structured response. It clearly explains the concept. The logic follows naturally from the first point.", signal, mood, {})

    assert incoherent.dimensions["coherence"] < coherent.dimensions["coherence"], \
        f"Incoherent({incoherent.dimensions['coherence']:.2f}) should be < Coherent({coherent.dimensions['coherence']:.2f})"
    print(f"  PASS: Coherence distinguishes (incoherent={incoherent.dimensions['coherence']:.2f} vs coherent={coherent.dimensions['coherence']:.2f})")


def test_reflector_emotional_appropriateness():
    engine = SelfReflectionEngine()
    signal = CognitionSignal()
    mood_stressed = {"mood": "stressed"}
    mood_playful = {"mood": "playful"}

    empathetic = engine.reflect("help", "I understand that's frustrating. Let me help.", signal, mood_stressed, {})
    joking = engine.reflect("help", "Haha that's funny!", signal, mood_playful, {})

    assert empathetic.dimensions["emotional_appropriateness"] > 0.5
    assert joking.dimensions["emotional_appropriateness"] > 0.5
    print(f"  PASS: Emotional appropriateness works (empathy={empathetic.dimensions['emotional_appropriateness']:.2f}, playful={joking.dimensions['emotional_appropriateness']:.2f})")


def test_reflector_awkwardness():
    engine = SelfReflectionEngine()
    signal = CognitionSignal()
    mood = {"mood": "neutral"}

    awkward = engine.reflect("hi", "Well, actually, like, basically you know, I think maybe perhaps sort of.", signal, mood, {})
    normal = engine.reflect("hi", "Hey, what's up?", signal, mood, {})

    assert awkward.dimensions["awkwardness"] < normal.dimensions["awkwardness"]
    print(f"  PASS: Awkwardness detection works (awkward={awkward.dimensions['awkwardness']:.2f} vs normal={normal.dimensions['awkwardness']:.2f})")


def test_reflector_grounding():
    engine = SelfReflectionEngine()
    signal = CognitionSignal()
    mood = {"mood": "neutral"}

    ungrounded = engine.reflect("search", "I searched the web and found...", signal, mood, {})
    grounded = engine.reflect("how", "Based on what you described, it sounds like...", signal, mood, {})

    assert ungrounded.dimensions["grounding"] < grounded.dimensions["grounding"]
    print(f"  PASS: Grounding detection works (ungrounded={ungrounded.dimensions['grounding']:.2f} vs grounded={grounded.dimensions['grounding']:.2f})")


def test_reflector_actionable_output():
    engine = SelfReflectionEngine()
    signal = CognitionSignal()
    mood = {"mood": "neutral"}

    obs = engine.reflect("hi", "Well like actually basically literally sort of you know maybe perhaps.", signal, mood, {})
    assert isinstance(obs.actionable, list)
    if obs.actionable:
        print(f"  PASS: Actionable suggestions generated: {obs.actionable[:2]}")
    else:
        print("  PASS: Actionable list is valid (empty)")


# ── ReflectionMemory Tests ───────────────────────────────────────────────────

from cognition.reflection.reflection_memory import ReflectionMemory


class TempReflectionStore:
    def __init__(self):
        self.data = {"observations": [], "version": 1}

    def load(self):
        return self.data

    def save(self, data):
        self.data = data


def test_reflection_store_and_retrieve():
    store = TempReflectionStore()
    mem = ReflectionMemory(store)
    obs = ReflectionObservation(dimensions={"coherence": 0.8}, overall_score=0.8)
    mem.add_observation(obs)

    recent = mem.get_recent(1)
    assert len(recent) == 1
    assert recent[0].overall_score == 0.8
    print("  PASS: Store and retrieve works")


def test_reflection_memory_cap():
    store = TempReflectionStore()
    mem = ReflectionMemory(store)
    for i in range(60):
        obs = ReflectionObservation(dimensions={"d": 0.5}, overall_score=0.5 + (i % 10) * 0.02)
        mem.add_observation(obs)

    assert len(mem.get_recent(100)) <= 50, f"Expected <= 50 observations, got {len(mem.get_recent(100))}"
    print(f"  PASS: Memory capped at 50 (has {len(mem.get_recent(50))} recent)")


def test_reflection_insights():
    store = TempReflectionStore()
    mem = ReflectionMemory(store)
    for i in range(5):
        obs = ReflectionObservation(
            dimensions={"coherence": 0.7, "verbosity_match": 0.6},
            overall_score=0.7,
            actionable=["reduce_verbosity"],
        )
        mem.add_observation(obs)

    insights = mem.get_insights()
    assert "overall_trend" in insights
    assert "actionable" in insights
    assert "reduce_verbosity" in insights["actionable"]
    print(f"  PASS: Insights generated: {insights['overall_trend']}")


def test_reflection_stability_indicators():
    store = TempReflectionStore()
    mem = ReflectionMemory(store)
    for i in range(5):
        obs = ReflectionObservation(dimensions={"d": 0.5}, overall_score=0.5 + i * 0.05)
        mem.add_observation(obs)

    indicators = mem.get_stability_indicators()
    assert "volatility" in indicators
    assert "total_reflections" in indicators
    print(f"  PASS: Stability indicators: volatility={indicators['volatility']}")


# ── PersonalityEngine Integration Tests ───────────────────────────────────────

def test_personality_engine_stabilization():
    pe = PersonalityEngine()
    assert pe.get_tone_modifiers() == {"warmth": 0.0, "verbosity": 0.0, "humor": 0.0, "formality": 0.0}

    pe.apply_stabilization({"warmth": 0.15, "verbosity": -0.1, "humor": 0.2, "formality": 0.0})
    mods = pe.get_tone_modifiers()
    assert mods["warmth"] == 0.15
    assert mods["verbosity"] == -0.1
    assert mods["humor"] == 0.2

    # Build prompt with behavioral context
    prompt = pe.build_system_prompt({"mood": {"mood": "neutral"}})
    assert "BEHAVIORAL CONTEXT" in prompt, "Behavioral context should be injected"
    assert "playful" in prompt.lower(), "Humor modifier should add playful tone"
    print("  PASS: Personality engine integrates behavioral context")


def test_personality_engine_no_modulation():
    pe = PersonalityEngine()
    prompt = pe.build_system_prompt({"mood": {"mood": "neutral"}})
    assert "BEHAVIORAL CONTEXT" not in prompt, "No modulation -> no behavioral section"
    print("  PASS: No behavioral section when no modulation applied")


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
        # Extractor
        test_extractor_positive_reaction,
        test_extractor_negative_reaction,
        test_extractor_correction,
        test_extractor_follow_up,
        test_extractor_empty_input,
        test_extractor_hinglish_reaction,
        test_extractor_no_previous_response,
        # Memory
        test_memory_update_and_retrieve,
        test_memory_confidence_grows,
        test_memory_context_key_differentiation,
        test_memory_cap_at_09,
        test_memory_min_observations,
        test_memory_decay,
        test_memory_serialization_roundtrip,
        test_memory_apply_reflection_insights,
        # Reinforcer
        test_reinforcer_zero_signal,
        test_reinforcer_positive_signal,
        test_reinforcer_saturation,
        # Stabilizer
        test_stabilizer_no_preferences,
        test_stabilizer_single_preference,
        test_stabilizer_caps,
        test_stabilizer_apply,
        test_stabilizer_drift_reset,
        # Self-reflection
        test_reflector_all_dimensions,
        test_reflector_coherence,
        test_reflector_emotional_appropriateness,
        test_reflector_awkwardness,
        test_reflector_grounding,
        test_reflector_actionable_output,
        # Reflection memory
        test_reflection_store_and_retrieve,
        test_reflection_memory_cap,
        test_reflection_insights,
        test_reflection_stability_indicators,
        # Personality integration
        test_personality_engine_stabilization,
        test_personality_engine_no_modulation,
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
    print(f"RESULTS: {passed}/{total} passed, {failed} failed")
    print(f"{'='*50}")
    return failed == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
