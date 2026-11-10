#!/usr/bin/env python
"""
Test script for YouTube media_play tool - FIXED VERSION
Tests the improved youtube_play function with proper typing and search
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from media_controller import get_media_controller

def test_youtube_play():
    """Test YouTube play with various queries"""
    
    mc = get_media_controller()
    
    print("=" * 70)
    print("TESTING YOUTUBE MEDIA_PLAY - FIXED VERSION")
    print("=" * 70)
    
    # Test query
    queries = [
        'honey singh songs',
        'trending music 2026',
        'lo-fi hip hop',
        'bollywood hits'
    ]
    
    print(f"\n📺 AVAILABLE TEST QUERIES:")
    for i, query in enumerate(queries, 1):
        print(f"   {i}. {query}")
    
    print("\n⚠️  NOTE: This test will open Chrome and YouTube")
    print("Make sure Chrome is installed and you're not busy!")
    
    choice = input("\nEnter query number to test (1-4) or custom query: ").strip()
    
    if choice in ['1', '2', '3', '4']:
        test_query = queries[int(choice) - 1]
    else:
        test_query = choice if choice else 'honey singh'
    
    print(f"\n▶️  Testing youtube_play('{test_query}')")
    print("-" * 70)
    
    result = mc.youtube_play(test_query)
    
    print("\n📊 RESULT:")
    print(f"   Success: {result.get('success')}")
    print(f"   Action: {result.get('action')}")
    print(f"   Query: {result.get('query')}")
    print(f"   Status: {result.get('status')}")
    if result.get('error'):
        print(f"   Error: {result.get('error')}")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    
    return result.get('success', False)

def test_spotify_play():
    """Test Spotify play"""
    
    mc = get_media_controller()
    
    print("\n" + "=" * 70)
    print("TESTING SPOTIFY MEDIA_PLAY")
    print("=" * 70)
    
    test_query = "tum hi ho"
    
    print(f"\n▶️  Testing spotify_play('{test_query}')")
    print("-" * 70)
    
    result = mc.spotify_play(test_query)
    
    print("\n📊 RESULT:")
    print(f"   Success: {result.get('success')}")
    print(f"   Action: {result.get('action')}")
    if result.get('error'):
        print(f"   Error: {result.get('error')}")
    
    print("\n" + "=" * 70)
    
    return result.get('success', False)

if __name__ == "__main__":
    print("\n🎵 MEDIA_PLAY TOOL - TESTING")
    print("This tool is used by 'media_play' to handle YouTube/Spotify playback\n")
    
    choice = input("Test YouTube (y) or Spotify (s)? [y/s]: ").strip().lower()
    
    if choice == 's':
        success = test_spotify_play()
    else:
        success = test_youtube_play()
    
    sys.exit(0 if success else 1)
