#!/bin/bash
# Lucy System Installer - Adds Lucy to PATH

echo "🚀 Installing Lucy System..."
echo ""

# Get absolute path
LUCY_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LUCY_BIN="$LUCY_DIR/lucy"

echo "Lucy location: $LUCY_DIR"
echo ""

# Create wrapper script in /usr/local/bin
WRAPPER="/usr/local/bin/lucy"

echo "Creating wrapper script..."
cat > "$WRAPPER" << EOF
#!/bin/bash
# Lucy Multi-Assistant System
cd "$LUCY_DIR"
/usr/local/bin/python3.11 "$LUCY_BIN" "\$@"
EOF

chmod +x "$WRAPPER"
chmod +x "$LUCY_BIN"

echo "✅ Lucy installed!"
echo ""
echo "Usage:"
echo "  lucy query \"your question\""
echo "  lucy stats"
echo "  lucy --help"
echo ""
echo "Test it:"
echo "  lucy stats"
echo ""

# Test
if command -v lucy &> /dev/null; then
    echo "✅ Lucy is in PATH and ready!"
else
    echo "⚠️  Lucy not in PATH. You may need to:"
    echo "   export PATH=\"/usr/local/bin:\$PATH\""
fi
