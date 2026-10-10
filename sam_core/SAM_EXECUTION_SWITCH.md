# Sam — перемикач виконання (схема, не live)

**Зараз:** `execution.default_mode=hitl_only`, `live_modes.auto_fx_crypto=false`, `auto_invest=false`.
Перемикач у JSON **не** є grant. Навіть `auto_fx_crypto=true` без `trade.execute` → лот не йде.

## Позиції

| Позиція | Хто крутить | Ефект |
|---|---|---|
| HITL only (default) | — | Кожен лот — кнопка Андрія |
| Auto FX+crypto @99 | Андрій, окремий HITL на права | Лоти FX/crypto якщо confluence ≥ 99, усі шари живі, RM зелений, рахунок demo або live за окремим прапором |
| Auto invest | **не існує** | Код `sam_auto_invest_allowed()` завжди False |

 Flip auto — `ActionClass.AUTHORITY_CHANGE` / `POLICY_CHANGE`. Таймаут = deny.

## Гейти auto (усі обов’язкові)

1. Перемикач ON.
2. Capability `trade.execute` видана (зараз ні).
3. Venue ∈ {forex, crypto}, не investment.
4. Confluence ≥ 99 **і** жоден шар `unavailable` **і** немає veto.
5. Hard SL, 1%/0.5% ризик, daily stop 3%, min R:R 2.5, news freeze, min lot 0.01.
6. Рахунок: demo XOR live згідно `account_mode`; live потребує `broker_live`.
7. Міст брокера відповідає; інакше `broker_unavailable`.

## 95 vs 99 vs LLM 0.99

- **95** — можна **показати** картку HITL.
- **99** — можна **розглянути** auto, якщо перемикач і grant.
- **LLM 0.99** — ігнорувати як дозвіл на гроші.

## Нічний auto

Лише позиція Auto FX+crypto. Інвестиції вночі не торгуються.
