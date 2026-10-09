# Transformation examples

Use these examples to learn decisions and structure. Do not copy their subject matter into other courses.

## Scattered bullets into a mechanism schema

Source slide:

```text
Pure Selective Re-transmission
- Rx ACKs each packet
- ACK additional PDUs after loss
- Tx sees a hole in ACKs
- Rx waits for the missing PDU
```

Preferred note:

```markdown
2. Pure Selective Re-transmission：只重传出错的包

    - **Mechanism**：Rx **ACKs each packet individually**（每个包独立确认）
    - **Handling Loss**：后续 PDU 仍会被确认，Tx 从 ACK 中看到一个 “hole”
    - **Buffering**：Rx 暂存后续包，补齐缺口后再按序交付
```

## Several slides into a comparison table

When architecture slides describe External, Conceptual, Internal, and Physical levels, combine them only if common dimensions are available:

```markdown
| 维度 | 层级 | 定义与功能 | 独立性体现 |
|---|---|---|---|
| 应用层 | **External** | 针对用户的定制化视图 | 一个用户视图的修改不影响其他用户 |
| 设计层 | **Conceptual** | 数据库的全局逻辑描述 | 逻辑结构可调整而尽量不影响用户视图 |
```

Do not invent a comparison column merely to make the table symmetric.

## API slides into a compact method table

```markdown
| 方法 | 作用 | 示例 |
|---|---|---|
| `int length()` | 返回字符串字符数 | `"Hello".length()` → `5` |
| `char charAt(int index)` | 返回指定索引的字符 | `"Hello".charAt(1)` → `'e'` |
```

Preserve exact signatures. One representative example is enough when variants share the same rule.

## Learning Outcome used only for audit

For `Explain candidate, primary, and foreign keys`, do not paste the outcome into `notes.md`. Check that all three are defined and distinguished, including uniqueness and irreducibility for a candidate key. Record missing coverage in `audit.md`.

## External supplement

```markdown
> 💡 **补充解释**
>
> Java 的动态绑定针对实例方法；静态方法和字段不按同一规则进行运行时分派。
```

Keep it separate because the supplied slide did not establish this claim.
