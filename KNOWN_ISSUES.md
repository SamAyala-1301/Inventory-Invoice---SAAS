# Known Issues - Sprint 1

## 1. Token Refresh Environment Variable Issue

**Status**: Known issue, non-critical

**Description**: Token refresh may have issues with environment variable tokenization.

**Impact**: Users might need to re-login after token expiry instead of auto-refresh.

**Workaround**: Manually login again when token expires.

**Fix Priority**: Sprint 1.1 (post-deployment hotfix)

---

## 2. Celery Email Sending Disabled

**Status**: Intentionally disabled for initial deployment

**Description**: Celery workers commented out in docker-compose.yml.

**Impact**: 
- Email verification not sent (users auto-verified)
- Invitation emails not sent (use invitation link from API)

**Workaround**: 
- Users are auto-verified on registration
- Invitation links can be copied from database or API response

**Fix Priority**: Sprint 2

---

## 3. Static Files Warning

**Status**: Minor warning, no functional impact

**Description**: `/app/static` directory warning in logs.

**Impact**: None - static files work correctly.

**Fix**: Create directory or update settings (optional).
