# PromptEvolver Testing Checklist

## 🔧 Phase 1: Basic Connectivity (30 min)

### Setup Steps:
- [ ] Run `chmod +x setup-dev.sh && ./setup-dev.sh`
- [ ] Copy Convex deployment URL to `.env.local`
- [ ] Verify `npm run dev` starts without errors
- [ ] Check browser console for connection errors

### Basic Tests:
- [ ] Page loads without TypeScript errors
- [ ] Convex client connects (no connection warnings)
- [ ] "System Health" button responds
- [ ] No 404 errors in network tab

## 🧪 Phase 2: Demo Data & UI (45 min)

### Seed Demo Data:
- [ ] Open Convex dashboard
- [ ] Run `seedData.seedDemoData({})` in functions tab
- [ ] Verify demo data created successfully
- [ ] Refresh frontend - session history should show data

### UI Component Tests:
- [ ] **Optimization Form**:
  - [ ] Quick/Advanced mode toggle works
  - [ ] Iteration slider appears in Advanced mode
  - [ ] Form validation (empty prompt)
  - [ ] Character counter updates

- [ ] **Session History Sidebar**:
  - [ ] Shows seeded demo sessions
  - [ ] Status badges display correctly
  - [ ] Quality scores visible
  - [ ] Session cards are clickable

- [ ] **Quality Metrics Dashboard**:
  - [ ] Appears when optimization completes
  - [ ] Progress bars animate correctly
  - [ ] Color coding works (red/yellow/blue/green)
  - [ ] Overall score displays

## 🚀 Phase 3: Core Functionality (60 min)

### Quick Optimization Flow:
- [ ] Enter test prompt: "Write a product description"
- [ ] Click "Quick Optimize"
- [ ] Progress modal appears
- [ ] Progress steps update in real-time
- [ ] Results modal shows after completion
- [ ] Session appears in history sidebar

### Advanced Optimization Flow:
- [ ] Switch to Advanced mode
- [ ] Set iterations to 3
- [ ] Enter test prompt: "Explain machine learning"
- [ ] Click "Start Advanced Optimization"
- [ ] Longer processing time (90-120s simulation)
- [ ] More detailed results
- [ ] Higher quality metrics

### Error Handling:
- [ ] Test with empty prompt (should show validation)
- [ ] Test with very long prompt (should handle gracefully)
- [ ] Simulate network error (disconnect internet briefly)
- [ ] Error toast appears and is dismissible

## 📱 Phase 4: Responsive & Polish (30 min)

### Responsive Design:
- [ ] Mobile view (< 768px)
  - [ ] Form stacks vertically
  - [ ] Sidebar becomes full-width
  - [ ] Modals are mobile-friendly
- [ ] Tablet view (768px - 1024px)
  - [ ] 2-column layout works
  - [ ] Touch interactions work
- [ ] Desktop view (> 1024px)
  - [ ] 3-column layout displays
  - [ ] All hover states work

### Animation & UX:
- [ ] Smooth transitions between states
- [ ] Loading spinners animate
- [ ] Progress bars fill smoothly
- [ ] Modal open/close animations
- [ ] Button hover effects work

## 🔍 Phase 5: Integration Testing (45 min)

### Real-time Updates:
- [ ] Start optimization in one tab
- [ ] Open another tab - progress should sync
- [ ] Complete optimization - both tabs update
- [ ] Session history updates in real-time

### Data Persistence:
- [ ] Refresh page during optimization
- [ ] State should restore correctly
- [ ] Session history persists
- [ ] Quality metrics remain visible

### Performance:
- [ ] Page loads quickly (< 3s)
- [ ] Optimization starts promptly
- [ ] No memory leaks (check dev tools)
- [ ] Smooth scrolling in session history

## 🐛 Common Issues to Watch For:

### Connection Issues:
- ❌ "Convex client not initialized"
- ❌ CORS errors in console
- ❌ 401/403 authentication errors
- ❌ WebSocket connection failures

### UI Issues:
- ❌ Layout breaks on mobile
- ❌ Modals don't center properly
- ❌ Progress bars don't animate
- ❌ Text overflow in session cards

### Functional Issues:
- ❌ Optimization never completes
- ❌ Progress gets stuck at certain steps
- ❌ Results modal shows undefined data
- ❌ Session history doesn't update

## ✅ Success Criteria:

**Phase 1 Success**: Page loads, Convex connects, no console errors
**Phase 2 Success**: Demo data loads, all UI components render correctly
**Phase 3 Success**: Both optimization modes work end-to-end
**Phase 4 Success**: Responsive design works on all screen sizes
**Phase 5 Success**: Real-time updates work, data persists correctly

## 🎯 Next Steps After Testing:

1. **If all tests pass**: Move to production deployment
2. **If issues found**: Debug systematically using this checklist
3. **Performance optimization**: Add code splitting, memoization
4. **Feature additions**: Export results, batch processing, etc.

---

**Testing Status**: ⏳ Ready to begin
**Last Updated**: $(date)
