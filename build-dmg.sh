#!/bin/sh

# install: "brew install create-dmg"
# Create a folder (named dmg) to prepare our DMG in (if it doesn't already exist).
mkdir -p dist/dmg
# Empty the dmg folder.
rm -r dist/dmg/*
# Copy the app bundle to the dmg folder.
cp -r "dist/TransForm.app" dist/dmg
# If the DMG already exists, delete it.
test -f "dist/TransForm.dmg" && rm "dist/TransForm.dmg"
create-dmg \
  --volname "TransForm" \
  --volicon "icons/app-light.icns" \
  --window-pos 200 120 \
  --window-size 600 300 \
  --icon-size 100 \
  --icon "TransForm.app" 175 120 \
  --hide-extension "TransForm.app" \
  --app-drop-link 425 120 \
  "dist/TransForm.dmg" \
  "dist/dmg/"