# DeSciOS noVNC Theme

This directory contains the complete DeSciOS theme for noVNC, transforming the default noVNC interface into a scientific computing environment with DeSciOS branding.

## 📁 Files Overview

### Core Theme Files
- **`vnc.html`** - Modified noVNC HTML with DeSciOS branding and theme integration
- **`descios-theme.css`** - Complete DeSciOS theme stylesheet with scientific color palette
- **`descios-icon.svg`** - Source SVG icon used to generate all favicon variants

### Icon Assets
- **`icons/`** - Directory containing all DeSciOS-themed favicon files:
  - 15 PNG files (16x16 to 192x192 pixels)
  - 2 SVG files (novnc-icon.svg, novnc-icon-sm.svg)

## 🎨 Theme Features

### Visual Branding
- **Logo**: "DeSciOS" replaces "noVNC" in both control bar and connect dialog
- **Title**: "DeSciOS Remote Desktop" 
- **Icons**: Custom scientific-themed favicons with DNA helix and molecular structures
- **Branding**: "DeSciOS v1.0" and "Scientific Computing Platform" overlays

### Color Scheme
- **Primary**: `#2E8B57` (Sea Green) - Scientific/research theme
- **Secondary**: `#4682B4` (Steel Blue) - Data visualization
- **Accent**: `#FFD700` (Gold) - Highlights and important elements
- **Background**: `#1C1C1C` (Dark) with gradient effects
- **Enhanced**: Glowing shadows, hover effects, pulse animations

## 🔧 Integration into Dockerfile

Add these commands to your Dockerfile after the noVNC installation:

```dockerfile
# Apply DeSciOS noVNC Theme
COPY novnc-theme/descios-theme.css /usr/share/novnc/app/styles/
COPY novnc-theme/vnc.html /usr/share/novnc/
COPY novnc-theme/icons/* /usr/share/novnc/app/images/icons/
```

## 📋 Manual Installation Steps

If applying to an existing container:

1. **Copy theme files**:
   ```bash
   docker cp novnc-theme/descios-theme.css container_name:/usr/share/novnc/app/styles/
   docker cp novnc-theme/vnc.html container_name:/usr/share/novnc/
   docker cp novnc-theme/icons/ container_name:/usr/share/novnc/app/images/
   ```

2. **No restart required** - Changes are live immediately via websockify

## 🧪 Technical Details

### CSS Architecture
- Uses CSS custom properties (variables) for consistent theming
- `!important` declarations to override default noVNC styles
- Responsive design with mobile-friendly adjustments
- Cache-busting with version parameters

### Icon Generation
- Source: `descios-icon.svg` (64x64 base design)
- Generated using ImageMagick: `convert descios-icon.svg -resize NxN output.png`
- Includes scientific elements: DNA helix, molecular structures, circuit patterns

### Browser Compatibility
- Modern browsers with CSS3 support
- Graceful degradation for older browsers
- Optimized for both desktop and mobile viewing

## 🚀 Verification

After installation, verify the theme by:
1. Accessing noVNC via browser
2. Check for "DeSciOS" branding in connect dialog
3. Verify DeSciOS favicon in browser tab
4. Confirm scientific color scheme is applied

## 📝 Customization

To modify the theme:
1. Edit `descios-theme.css` for styling changes
2. Update CSS custom properties in `:root` section for color scheme
3. Regenerate icons from `descios-icon.svg` if needed
4. Update cache-busting version in `vnc.html` after changes

---

**Created for DeSciOS v1.0 - Scientific Computing Platform** 