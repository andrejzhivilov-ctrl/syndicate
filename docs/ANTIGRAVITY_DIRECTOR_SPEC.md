# Знята з дії специфікація Antigravity Director

> **Статус: застарілий, неавторитетний проєктний документ.** Попередня редакція помилково описувала `antigravity` як окрему активну агентку з автономними можливостями та grants. Ці твердження відкликані: вони не є дозволами, чинною архітектурою або інструкцією до розгортання.

## Чинна ідентичність

- **Агентка:** Аліса (`agent_id: alice`).
- **Технологія виконання:** Antigravity SDK (`runtime: antigravity_sdk`), а не окрема агентка.
- **Канонічний профіль:** [`config/agents/alice.profile.json`](../config/agents/alice.profile.json).
- **Технічний опис runtime:** [`docs/ALICE_RUNTIME.md`](ALICE_RUNTIME.md).
- **Стан:** `prepared_not_enabled`; модель не вибрана, capabilities, grants, resource scopes і services порожні.

## Межі та сумісність

Старий незалежний Antigravity director не реєструється в `deploy/runtime/director_runner.py`. Його імпорт-сумісний клас залишено лише як безопераційний placeholder з дією `capabilities`; жодної браузерної автоматизації, виконання команд, GitHub-дій, запуску субагентів чи інших зовнішніх операцій він не надає.

`config/agents/antigravity.live_profile.json` збережено як явний retired compatibility alias, що вказує на Алісу й не має capabilities або grants. Старий Compose service ізольований профілем `antigravity-legacy-disabled`, а не загальним профілем `directors`. Згенерована policy `eva-antigravity` не має Vault data/metadata grants; вона містить лише self-lookup/self-renew токена. Це декларація коду, а не твердження про стан live Vault.

Цей файл збережено як пояснення міграції, а не як специфікацію для реалізації чи запуску. Жодної зміни live Vault, серверу, бази даних або контейнерів не виконувалося.
