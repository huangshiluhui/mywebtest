# Vue 中 `<style lang="scss">` 详解

## 一、`lang` 属性的作用

`lang` 属性用于指定 `<style>` 标签中使用的样式语言。

### 默认情况

如果不指定 `lang`，默认使用 **CSS**：

```vue
<style>
/* 这是普通的 CSS */
.login {
  color: red;
}
</style>
```

### 指定语言

使用 `lang` 属性可以指定其他样式语言：

```vue
<style lang="scss">
/* 这是 SCSS 语法 */
</style>

<style lang="sass">
/* 这是 SASS 语法 */
</style>

<style lang="less">
/* 这是 Less 语法 */
</style>

<style lang="stylus">
/* 这是 Stylus 语法 */
</style>
```

## 二、SCSS 是什么？

### SCSS (Sassy CSS)

**SCSS** 是 **Sass (Syntactically Awesome StyleSheets)** 的一种语法格式。

- **Sass** 有两种语法：
  1. **SCSS**（Sassy CSS）- 使用大括号和分号，类似 CSS
  2. **Sass**（缩进语法）- 不使用大括号和分号，使用缩进

- **SCSS** 是 CSS 的超集，所有有效的 CSS 都是有效的 SCSS

### SCSS 的特点

1. **完全兼容 CSS**
   - 可以直接写 CSS 代码
   - 浏览器最终看到的还是 CSS

2. **提供额外功能**
   - 嵌套（Nesting）
   - 变量（Variables）
   - 混合（Mixins）
   - 函数（Functions）
   - 继承（Inheritance）

## 三、SCSS vs CSS 对比

### 示例1：嵌套（Nesting）

**CSS（普通写法）**：
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

**SCSS（嵌套写法）**：
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
- ✅ 代码更清晰，结构更直观
- ✅ 减少重复书写父选择器
- ✅ 更容易维护

### 示例2：变量（Variables）

**CSS（没有变量）**：
```css
.title {
  color: #707070;
}

.login-tip {
  color: #707070;
}
```

**SCSS（使用变量）**：
```scss
$text-color: #707070;

.title {
  color: $text-color;
}

.login-tip {
  color: $text-color;
}
```

**优势**：
- ✅ 统一管理颜色、字体等
- ✅ 修改一处，全局生效
- ✅ 提高可维护性

### 示例3：混合（Mixins）

**CSS（重复代码）**：
```css
.button-primary {
  padding: 10px 20px;
  border-radius: 4px;
  background: #409eff;
  color: white;
}

.button-success {
  padding: 10px 20px;
  border-radius: 4px;
  background: #67c23a;
  color: white;
}
```

**SCSS（使用 Mixin）**：
```scss
@mixin button-style($bg-color) {
  padding: 10px 20px;
  border-radius: 4px;
  background: $bg-color;
  color: white;
}

.button-primary {
  @include button-style(#409eff);
}

.button-success {
  @include button-style(#67c23a);
}
```

**优势**：
- ✅ 减少重复代码
- ✅ 提高代码复用性

## 四、当前项目中的使用

### LoginView.vue 中的 SCSS

```vue
<style lang="scss" scoped>
.login-form {
  border-radius: 6px;
  background: #ffffff;
  width: 400px;
  padding: 25px 25px 5px 25px;

  .el-input {  // ← 嵌套语法
    height: 40px;

    input {  // ← 嵌套语法
      display: inline-block;
      height: 40px;
    }
  }
}
</style>
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

## 五、`scoped` 的作用

### `scoped` 属性

`scoped` 表示样式只作用于当前组件，不会影响其他组件。

**没有 `scoped`**：
```vue
<style>
.title {
  color: red;
}
</style>
```
- ❌ 会影响所有组件中的 `.title` 类

**有 `scoped`**：
```vue
<style scoped>
.title {
  color: red;
}
</style>
```
- ✅ 只影响当前组件中的 `.title` 类

### `scoped` 的工作原理

Vue 会自动为每个组件添加唯一的属性选择器：

**编译前**：
```vue
<template>
  <h3 class="title">标题</h3>
</template>

<style scoped>
.title {
  color: red;
}
</style>
```

**编译后**：
```html
<h3 class="title" data-v-7ba5bd90>标题</h3>
```

```css
.title[data-v-7ba5bd90] {
  color: red;
}
```

## 六、完整的属性说明

```vue
<style lang="scss" scoped>
```

- **`lang="scss"`**：指定使用 SCSS 语法
- **`scoped`**：样式只作用于当前组件

### 其他组合

```vue
<!-- 普通 CSS，作用域限制 -->
<style scoped>
</style>

<!-- SCSS，全局样式 -->
<style lang="scss">
</style>

<!-- SCSS，作用域限制 -->
<style lang="scss" scoped>
</style>
```

## 七、为什么使用 SCSS？

### 优势

1. **代码更简洁**
   - 嵌套语法减少重复
   - 结构更清晰

2. **更易维护**
   - 变量统一管理
   - 修改更方便

3. **功能更强大**
   - Mixins、Functions 等高级特性
   - 提高开发效率

### 注意事项

1. **需要安装依赖**
   ```bash
   npm install sass sass-loader --save-dev
   ```

2. **编译时间**
   - SCSS 需要编译成 CSS
   - 编译时间略长（通常可忽略）

3. **浏览器兼容性**
   - SCSS 最终编译成 CSS
   - 浏览器兼容性与 CSS 相同

## 八、实际项目建议

### 推荐使用 SCSS 的场景

- ✅ 大型项目（需要更好的代码组织）
- ✅ 需要统一管理样式变量
- ✅ 需要复用样式代码（Mixins）

### 可以使用普通 CSS 的场景

- ✅ 小型项目
- ✅ 样式简单
- ✅ 不需要 SCSS 的高级特性

## 总结

### `lang="scss"` 的含义

- **`lang`**：指定样式语言
- **`scss`**：使用 SCSS 语法（Sass 的一种格式）

### 关键理解

1. **SCSS 是 CSS 的超集**
   - 可以写普通 CSS
   - 也可以使用 SCSS 的高级特性

2. **最终都会编译成 CSS**
   - 浏览器只认识 CSS
   - SCSS 在构建时编译

3. **`scoped` 是独立的**
   - 与 `lang` 无关
   - 用于限制样式作用域

### 记忆要点

> **`lang="scss"` = 使用 SCSS 语法编写样式**  
> **`scoped` = 样式只作用于当前组件**  
> **SCSS = CSS + 嵌套 + 变量 + Mixins + 更多功能**
