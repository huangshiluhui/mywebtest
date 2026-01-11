# SCSS 语法详解

## 一、SCSS 简介

**SCSS (Sassy CSS)** 是 Sass 的一种语法格式，是 CSS 的超集。

- ✅ 所有有效的 CSS 都是有效的 SCSS
- ✅ 提供嵌套、变量、混合等高级特性
- ✅ 最终编译成普通 CSS

## 二、核心语法特性

### 1. 嵌套（Nesting）

**最常用的 SCSS 特性**，可以嵌套选择器。

#### CSS 写法（普通）
```css
.login-form {
  border-radius: 6px;
  background: #ffffff;
}

.login-form .el-input {
  height: 40px;
}

.login-form .el-input input {
  display: inline-block;
}
```

#### SCSS 写法（嵌套）
```scss
.login-form {
  border-radius: 6px;
  background: #ffffff;
  
  .el-input {
    height: 40px;
    
    input {
      display: inline-block;
    }
  }
}
```

**优势**：
- ✅ 代码结构更清晰
- ✅ 减少重复书写父选择器
- ✅ 更容易维护

#### 嵌套伪类和伪元素
```scss
.button {
  color: blue;
  
  &:hover {  // & 代表父选择器
    color: red;
  }
  
  &:active {
    color: green;
  }
  
  &::before {
    content: "";
  }
}
```

**编译后**：
```css
.button {
  color: blue;
}

.button:hover {
  color: red;
}

.button:active {
  color: green;
}

.button::before {
  content: "";
}
```

### 2. 变量（Variables）

使用 `$` 符号定义变量。

#### 基本用法
```scss
// 定义变量
$primary-color: #409eff;
$font-size: 16px;
$border-radius: 4px;

// 使用变量
.button {
  background: $primary-color;
  font-size: $font-size;
  border-radius: $border-radius;
}
```

**编译后**：
```css
.button {
  background: #409eff;
  font-size: 16px;
  border-radius: 4px;
}
```

#### 变量作用域
```scss
$global-color: red;  // 全局变量

.container {
  $local-color: blue;  // 局部变量
  
  .item {
    color: $global-color;  // 可以使用全局变量
    background: $local-color;  // 可以使用局部变量
  }
}

.other {
  color: $global-color;  // ✅ 可以使用
  // background: $local-color;  // ❌ 错误，局部变量不可用
}
```

### 3. 混合（Mixins）

使用 `@mixin` 定义可复用的样式块，使用 `@include` 引入。

#### 基本用法
```scss
// 定义 Mixin
@mixin button-style {
  padding: 10px 20px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
}

// 使用 Mixin
.button-primary {
  @include button-style;
  background: #409eff;
  color: white;
}

.button-success {
  @include button-style;
  background: #67c23a;
  color: white;
}
```

**编译后**：
```css
.button-primary {
  padding: 10px 20px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  background: #409eff;
  color: white;
}

.button-success {
  padding: 10px 20px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  background: #67c23a;
  color: white;
}
```

#### 带参数的 Mixin
```scss
@mixin button-style($bg-color, $text-color: white) {
  padding: 10px 20px;
  border-radius: 4px;
  background: $bg-color;
  color: $text-color;
}

.button-primary {
  @include button-style(#409eff);  // 使用默认的 white
}

.button-danger {
  @include button-style(#f56c6c, #fff);  // 指定两个参数
}
```

### 4. 继承（Inheritance）

使用 `@extend` 继承其他选择器的样式。

```scss
.message {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.success {
  @extend .message;
  background: #67c23a;
  color: white;
}

.error {
  @extend .message;
  background: #f56c6c;
  color: white;
}
```

**编译后**：
```css
.message, .success, .error {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.success {
  background: #67c23a;
  color: white;
}

.error {
  background: #f56c6c;
  color: white;
}
```

### 5. 函数（Functions）

SCSS 提供了很多内置函数，也可以自定义函数。

#### 内置函数示例
```scss
$primary-color: #409eff;

.button {
  // 颜色函数
  background: lighten($primary-color, 10%);  // 变亮
  border-color: darken($primary-color, 10%);  // 变暗
  
  // 数学函数
  width: percentage(2/3);  // 66.666667%
  margin: round(3.7px);  // 4px
  
  // 字符串函数
  font-family: quote(Arial);  // "Arial"
}
```

#### 自定义函数
```scss
@function calculate-width($base, $multiplier) {
  @return $base * $multiplier;
}

.container {
  width: calculate-width(100px, 2);  // 200px
}
```

### 6. 运算（Operations）

SCSS 支持数学运算。

```scss
$base-size: 16px;
$padding: 20px;

.container {
  font-size: $base-size * 1.5;  // 24px
  padding: $padding / 2;  // 10px
  margin: $base-size + $padding;  // 36px
  width: 100% - 20px;  // 80%
}
```

### 7. 条件语句（Control Directives）

#### @if, @else if, @else
```scss
$theme: dark;

.button {
  @if $theme == dark {
    background: #333;
    color: white;
  } @else if $theme == light {
    background: #fff;
    color: #333;
  } @else {
    background: #409eff;
    color: white;
  }
}
```

#### @for 循环
```scss
@for $i from 1 through 3 {
  .item-#{$i} {
    width: 100px * $i;
  }
}
```

**编译后**：
```css
.item-1 {
  width: 100px;
}

.item-2 {
  width: 200px;
}

.item-3 {
  width: 300px;
}
```

#### @each 循环
```scss
$colors: red, green, blue;

@each $color in $colors {
  .text-#{$color} {
    color: $color;
  }
}
```

**编译后**：
```css
.text-red {
  color: red;
}

.text-green {
  color: green;
}

.text-blue {
  color: blue;
}
```

### 8. 插值（Interpolation）

使用 `#{}` 在字符串中插入变量。

```scss
$name: "button";
$side: "top";

.#{$name} {
  margin-#{$side}: 10px;
}
```

**编译后**：
```css
.button {
  margin-top: 10px;
}
```

## 三、实际项目示例

### 示例1：你的 LoginView.vue 中的 SCSS

```scss
.login-form {
  border-radius: 6px;
  background: #ffffff;
  width: 400px;
  padding: 25px 25px 5px 25px;

  .el-input {  // ← 嵌套
    height: 40px;

    input {  // ← 嵌套
      display: inline-block;
      height: 40px;
    }
  }
}
```

**编译后的 CSS**：
```css
.login-form {
  border-radius: 6px;
  background: #ffffff;
  width: 400px;
  padding: 25px 25px 5px 25px;
}

.login-form .el-input {
  height: 40px;
}

.login-form .el-input input {
  display: inline-block;
  height: 40px;
}
```

### 示例2：使用变量优化

```scss
// 定义变量
$primary-color: #409eff;
$text-color: #707070;
$border-radius: 6px;
$spacing: 25px;

.login-form {
  border-radius: $border-radius;
  background: #ffffff;
  padding: $spacing;
  
  .title {
    color: $text-color;
  }
  
  .el-button {
    background: $primary-color;
  }
}
```

### 示例3：使用 Mixin 复用样式

```scss
// 定义 Mixin
@mixin flex-center {
  display: flex;
  justify-content: center;
  align-items: center;
}

@mixin input-style {
  height: 40px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

// 使用
.login {
  @include flex-center;
  height: 100%;
}

.login-form {
  .el-input {
    @include input-style;
  }
}
```

## 四、SCSS vs CSS 对比表

| 特性 | CSS | SCSS |
|------|-----|------|
| 嵌套 | ❌ 不支持 | ✅ 支持 |
| 变量 | ❌ 不支持（CSS 变量有限） | ✅ 支持 `$variable` |
| 混合 | ❌ 不支持 | ✅ 支持 `@mixin` |
| 继承 | ❌ 不支持 | ✅ 支持 `@extend` |
| 函数 | ❌ 不支持 | ✅ 支持内置和自定义函数 |
| 运算 | ❌ 不支持 | ✅ 支持数学运算 |
| 条件语句 | ❌ 不支持 | ✅ 支持 `@if`, `@for`, `@each` |

## 五、常用 SCSS 模式

### 1. BEM 命名 + SCSS 嵌套

```scss
.block {
  &__element {  // .block__element
    color: red;
    
    &--modifier {  // .block__element--modifier
      color: blue;
    }
  }
}
```

### 2. 响应式设计

```scss
$breakpoints: (
  mobile: 480px,
  tablet: 768px,
  desktop: 1024px
);

@mixin respond-to($breakpoint) {
  @media (min-width: map-get($breakpoints, $breakpoint)) {
    @content;
  }
}

.container {
  width: 100%;
  
  @include respond-to(tablet) {
    width: 750px;
  }
  
  @include respond-to(desktop) {
    width: 1200px;
  }
}
```

### 3. 主题切换

```scss
$themes: (
  light: (
    bg: #fff,
    text: #333
  ),
  dark: (
    bg: #333,
    text: #fff
  )
);

@mixin theme($theme-name) {
  $theme: map-get($themes, $theme-name);
  
  background: map-get($theme, bg);
  color: map-get($theme, text);
}

.container {
  @include theme(light);
}
```

## 六、注意事项

### 1. 嵌套不要过深

❌ **不推荐**（嵌套过深）：
```scss
.container {
  .wrapper {
    .content {
      .item {
        .title {
          // 嵌套太深，难以维护
        }
      }
    }
  }
}
```

✅ **推荐**（适度嵌套）：
```scss
.container {
  // ...
}

.container-content {
  // ...
}

.container-item-title {
  // ...
}
```

### 2. 变量命名规范

```scss
// ✅ 推荐：使用有意义的名称
$primary-color: #409eff;
$font-size-large: 18px;

// ❌ 不推荐：名称不清晰
$color1: #409eff;
$size: 18px;
```

### 3. Mixin 不要过度使用

- ✅ 用于真正需要复用的样式
- ❌ 不要为每个小样式都创建 Mixin

## 七、总结

### SCSS 核心语法

1. **嵌套**：`选择器 { 嵌套选择器 { } }`
2. **变量**：`$variable: value;`
3. **混合**：`@mixin name { }` 和 `@include name;`
4. **继承**：`@extend .class;`
5. **函数**：`@function name() { @return value; }`
6. **运算**：支持 `+`, `-`, `*`, `/`, `%`
7. **条件**：`@if`, `@for`, `@each`
8. **插值**：`#{$variable}`

### 关键要点

> **SCSS = CSS + 编程语言特性**  
> **所有 SCSS 最终编译成 CSS**  
> **嵌套是最常用的特性**  
> **变量和 Mixin 提高代码复用性**

### 学习建议

1. 从嵌套开始（最常用）
2. 学习变量（统一管理样式）
3. 掌握 Mixin（代码复用）
4. 根据需要学习其他高级特性
