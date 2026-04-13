package com.example.saapp.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.example.saapp.vo.SysEmployee;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;

@Mapper
public interface SysEmployeeMapper extends BaseMapper<SysEmployee> {
    @Select("SELECT e.id, e.emp_name, e.gender, e.age, e.dept_id, e.salary, e.status, e.create_time, e.update_time, " +
	    "d.dept_name AS dept_name " +
	    "FROM sys_employee e " +
	    "LEFT JOIN sys_dept d ON e.dept_id = d.id " +
	    "ORDER BY e.id")
    List<SysEmployee> selectEmployeeList();

    @Select("SELECT e.id, e.emp_name, e.gender, e.age, e.dept_id, e.salary, e.status, e.create_time, e.update_time, " +
	    "d.dept_name AS dept_name " +
	    "FROM sys_employee e " +
	    "LEFT JOIN sys_dept d ON e.dept_id = d.id " +
	    "WHERE e.id = #{id}")
    SysEmployee selectEmployeeById(@Param("id") Long id);
}