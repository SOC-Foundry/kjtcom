#!/usr/bin/env fish
# Install pipeline dependencies for kjtcom
# Run from repo root: fish requirements/install.fish

echo "Installing Python dependencies..."
pip install --user faster-whisper google-generativeai firebase-admin

echo "Installing Node dependencies for Cloud Functions..."
cd functions
npm install
cd ..

echo "Verifying tools..."
python3 --version
firebase --version
yt-dlp --version
flutter --version

echo "Done. Run 'nvidia-smi' to verify CUDA."
