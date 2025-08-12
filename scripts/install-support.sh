#!/bin/bash

echo "Installing support widget dependencies..."

# Navigate to Angular frontend
cd angular-frontend

# Install additional Angular Material components for support widget
npm install @angular/material@^17.0.0 --save

# Install additional dependencies for enhanced functionality
npm install @angular/cdk@^17.0.0 --save

echo "Support widget dependencies installed successfully!"

# Create assets directory if it doesn't exist
mkdir -p src/assets

# Create default support agent avatar
echo "Creating default support agent avatar..."
cat > src/assets/support-agent.svg << 'EOF'
<svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
<circle cx="20" cy="20" r="20" fill="#2196F3"/>
<svg x="8" y="8" width="24" height="24" viewBox="0 0 24 24" fill="white">
<path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
</svg>
</svg>
EOF

echo "Support widget setup complete!"
echo ""
echo "To use the support widget:"
echo "1. The widget will appear as a floating button in the bottom-right corner"
echo "2. Users can chat, browse help articles, and submit support tickets"
echo "3. The system includes AI-powered responses and contextual help"
echo "4. Notifications will show when there are unread messages"
echo ""
echo "Features included:"
echo "✅ Live chat with AI responses"
echo "✅ Searchable help articles"
echo "✅ Support ticket submission"
echo "✅ System information collection"
echo "✅ Mobile responsive design"
echo "✅ Notification system"
echo "✅ Satisfaction surveys"
